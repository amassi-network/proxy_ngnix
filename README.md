# proxy_ngnix


Gestionnaire Django de proxys HTTPS avec Nginx
Crée une application Python utilisant Django 4.2+, conçue pour s’exécuter avec des privilèges root sur un serveur Linux (Debian/Ubuntu).
L’application expose une interface d’administration sécurisée via HTTPS sur le port 8080.

🎯 Objectif
Cette application web permet à des administrateurs de gérer dynamiquement des configurations de proxys HTTPS via Nginx.
Elle autorise la création, la modification et la suppression de redirections HTTPS par nom de domaine, avec gestion complète des certificats SSL associés.

🔐 Authentification
Authentification des utilisateurs via le système natif de Django.

Stockage des identifiants dans une base MySQL.

Accès à l'interface restreint aux utilisateurs authentifiés.

🌐 Fonctionnalités principales
1. Gestion des proxys HTTPS
Chaque proxy configuré inclut :

Nom de domaine (ex : example.com)

URL de backend HTTP ou HTTPS (ex : http://localhost:3000)

État actif/inactif

2. Gestion des certificats SSL (via formulaire web)
L’interface web Django permet à l’administrateur de coller directement le contenu PEM de 3 composants dans un formulaire :

Clé privée SSL : -----BEGIN PRIVATE KEY-----

Certificat principal : -----BEGIN CERTIFICATE-----

Chaîne intermédiaire (SSL bundle) : également au format PEM

Validation :

Vérifier que chaque champ commence par le bon en-tête PEM.

Refuser ou alerter en cas de champ vide ou malformé.

À l’enregistrement :

Créer le dossier /etc/nginx/certs/<domain>/

Sauvegarder les fichiers respectivement en :

privkey.pem

cert.pem

chain.pem

Extraire la date d’expiration du cert.pem via Python (ssl ou OpenSSL.crypto) et la stocker en base.

Recharger Nginx avec systemctl reload nginx.

3. Génération automatique de la configuration Nginx
Pour chaque domaine :

Générer un fichier /etc/nginx/sites-enabled/<domain>.conf avec :

redirection HTTPS → backend

certificat, clé privée et chaîne intermédiaire

Supprimer ou désactiver le fichier pour désactiver un proxy

Recharger automatiquement Nginx à chaque modification

4. Tableau de bord & alertes
Affichage de la liste des domaines, leur statut (actif/inactif), backend, date d’expiration du certificat

Alerte visuelle si expiration dans :

Moins de 30 jours → alerte orange

Moins de 10 jours → alerte rouge

Prévoir structure future pour :

Envoi d’emails d’alerte

Webhooks ou intégration Slack

5. Suivi du trafic (facultatif mais recommandé)
À partir des logs Nginx (/var/log/nginx/<domain>.access.log) :

Nombre de requêtes

Volume de bande passante transférée

Date du dernier accès

📁 Arborescence attendue
swift
Copier
Modifier
/etc/nginx/sites-enabled/<domain>.conf
/etc/nginx/certs/<domain>/privkey.pem
/etc/nginx/certs/<domain>/cert.pem
/etc/nginx/certs/<domain>/chain.pem
⚙️ Contraintes techniques
L’interface Django tourne en HTTPS sur :8080 (certificat auto-signé ou Let’s Encrypt).

L’application tourne avec les privilèges nécessaires pour :

Lire/écrire dans /etc/nginx/

Sauvegarder les certificats

Recharger le service Nginx

📦 Stack technologique
Python 3.11+

Django 4.2+

MySQL

Nginx

(Optionnel) Bootstrap pour une interface plus esthétique

Bibliothèques Python :

ssl, OpenSSL, os, subprocess

datetime pour la gestion des dates
