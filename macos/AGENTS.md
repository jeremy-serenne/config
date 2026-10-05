# Remettre le Mac en service

Charger ce document pour installer ou maintenir le setup macOS. Ne pas exécuter un bootstrap sur une autre plateforme.

1. Lire le README racine et [manual-steps.md](manual-steps.md). Inventorier les fichiers existants et les apps ; le bootstrap est adapté à un nouveau Mac, pas à la migration silencieuse de configs existantes.
2. Vérifier `xcode-select -p`. Si absent, lancer `xcode-select --install` et laisser l'utilisateur terminer la fenêtre macOS avant de continuer.
3. Vérifier Homebrew dans `/opt/homebrew/bin/brew` ou `/usr/local/bin/brew`. Si absent, suivre la procédure officielle https://brew.sh ; laisser l'utilisateur saisir lui-même les demandes de mot de passe.
4. Exécuter `bash macos/bootstrap.sh`. Résoudre chaque conflit affiché en comparant les fichiers ; ne pas remplacer une config sans examiner les différences.
5. Guider la connexion à GitHub avec `gh auth login`, puis le reste des étapes humaines. Ne pas afficher de token ni copier les credentials dans le dépôt.
6. Exécuter `bash macos/verify.sh`. Traiter les échecs. Ouvrir xbar et vérifier visuellement son menu PR, l'agenda dans Raycast et les autres apps utiles. Une sortie de script valide ne prouve pas un affichage dans la barre.
7. Installer ensuite les extras avec `bash macos/bootstrap.sh --extras`, puis `bash macos/verify.sh --extras`. Les gros logiciels et accès professionnels sont décrits dans manual-steps.md.
8. Rapporter ce qui fonctionne, les conflits et les étapes encore non réalisées. Ne pas déclarer le Mac opérationnel sur le seul résultat du bootstrap : valider les accès et au moins un projet réel.

Le bootstrap est réexécutable. Pour reprendre, le relancer : paquets déjà installés et fichiers identiques sont conservés. Préférer les outils API/CLI aux clics lorsque disponibles. Préfixer les commandes shell avec `rtk` lorsqu'il est installé (`rtk proxy` pour une commande non prise en charge) ; il n'est pas un prérequis au démarrage.

Pour maintenir ce dossier : validation syntaxique shell/zsh et Python, validation des Brewfiles, tests des conflits/réexécution dans des dossiers temporaires, et contrôle de l'absence de secrets avant push. Ne pas tester l'installation complète sur le Mac courant sans demande explicite.
