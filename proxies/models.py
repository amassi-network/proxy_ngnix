from datetime import datetime
import os
import ssl
import subprocess

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Proxy(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    backend = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    private_key = models.TextField(help_text='-----BEGIN PRIVATE KEY-----')
    certificate = models.TextField(help_text='-----BEGIN CERTIFICATE-----')
    chain = models.TextField(help_text='-----BEGIN CERTIFICATE-----')

    cert_expiration = models.DateTimeField(null=True, blank=True)
    request_count = models.BigIntegerField(default=0)
    bandwidth = models.BigIntegerField(default=0)
    last_access = models.DateTimeField(null=True, blank=True)

    def clean(self):
        errors = {}
        if not self.private_key.strip().startswith('-----BEGIN'):
            errors['private_key'] = 'Clé privée invalide.'
        if not self.certificate.strip().startswith('-----BEGIN CERTIFICATE-----'):
            errors['certificate'] = 'Certificat invalide.'
        if not self.chain.strip().startswith('-----BEGIN'):
            errors['chain'] = 'Chaîne intermédiaire invalide.'
        if errors:
            raise ValidationError(errors)
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        base_cert_dir = getattr(settings, 'NGINX_CERT_DIR', '/etc/nginx/certs')
        base_sites_dir = getattr(settings, 'NGINX_SITES_DIR', '/etc/nginx/sites-enabled')
        domain_dir = os.path.join(base_cert_dir, self.domain)
        os.makedirs(domain_dir, exist_ok=True)
        with open(os.path.join(domain_dir, 'privkey.pem'), 'w') as f:
            f.write(self.private_key)
        with open(os.path.join(domain_dir, 'cert.pem'), 'w') as f:
            f.write(self.certificate)
        with open(os.path.join(domain_dir, 'chain.pem'), 'w') as f:
            f.write(self.chain)
        cert_path = os.path.join(domain_dir, 'cert.pem')
        try:
            info = ssl._ssl._test_decode_cert(cert_path)
            not_after = info.get('notAfter')
            self.cert_expiration = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
            super().save(update_fields=['cert_expiration'])
        except Exception:
            pass
        conf_path = os.path.join(base_sites_dir, f'{self.domain}.conf')
        server_block = f"""
server {
    listen 443 ssl;
    server_name {self.domain};
    ssl_certificate {os.path.join(domain_dir, 'cert.pem')};
    ssl_certificate_key {os.path.join(domain_dir, 'privkey.pem')};
    ssl_trusted_certificate {os.path.join(domain_dir, 'chain.pem')};
    location / {{
        proxy_pass {self.backend};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }}
}
"""
        if self.active:
            os.makedirs(base_sites_dir, exist_ok=True)
            with open(conf_path, 'w') as f:
                f.write(server_block)
        else:
            if os.path.exists(conf_path):
                os.remove(conf_path)
        try:
            subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        except Exception:
            pass

    def update_stats(self):
        log_path = f'/var/log/nginx/{self.domain}.access.log'
        if not os.path.exists(log_path):
            return
        requests = 0
        bandwidth = 0
        last_access = None
        with open(log_path) as fh:
            for line in fh:
                requests += 1
                parts = line.split()
                if len(parts) > 9:
                    try:
                        bandwidth += int(parts[9])
                    except ValueError:
                        pass
                if len(parts) > 3:
                    try:
                        last_access = datetime.strptime(parts[3][1:], '%d/%b/%Y:%H:%M:%S')
                    except Exception:
                        pass
        self.request_count = requests
        self.bandwidth = bandwidth
        self.last_access = last_access
        super().save(update_fields=['request_count', 'bandwidth', 'last_access'])

    def __str__(self):
        return self.domain
