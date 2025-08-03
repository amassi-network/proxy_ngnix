from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ProxyForm
from .models import Proxy

@login_required
def dashboard(request):
    proxies = Proxy.objects.all()
    now = timezone.now()
    for p in proxies:
        if p.cert_expiration:
            delta = (p.cert_expiration - now).days
            if delta < 10:
                p.alert = 'danger'
            elif delta < 30:
                p.alert = 'warning'
            else:
                p.alert = 'success'
        else:
            p.alert = 'secondary'
    return render(request, 'proxies/dashboard.html', {'proxies': proxies})

@login_required
def proxy_create(request):
    if request.method == 'POST':
        form = ProxyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProxyForm()
    return render(request, 'proxies/form.html', {'form': form})

@login_required
def proxy_edit(request, pk):
    proxy = Proxy.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProxyForm(request.POST, instance=proxy)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProxyForm(instance=proxy)
    return render(request, 'proxies/form.html', {'form': form})

@login_required
def proxy_delete(request, pk):
    proxy = Proxy.objects.get(pk=pk)
    if request.method == 'POST':
        proxy.delete()
        return redirect('dashboard')
    return render(request, 'proxies/delete.html', {'proxy': proxy})
