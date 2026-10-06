# Étapes humaines et état de la capture

À lire pour terminer une installation ou compléter le setup. Cocher dans une note locale, pas avec des données personnelles dans ce dépôt public.

## Essentiel

- Se connecter à Bitwarden et récupérer les accès nécessaires ; ne pas exporter le coffre dans le dépôt.
- Se connecter à Codex, Firefox, Slack, Linear et JetBrains. Activer les licences.
- GitHub : `gh auth login --hostname github.com`, puis `gh auth setup-git` pour les dépôts HTTPS. Les clés SSH privées restent hors du dépôt ; créer/enregistrer une clé si les projets utilisent SSH.
- Définir l'identité Git locale : `git config --global user.name jeremy-serenne` et `git config --global user.email <email choisi>`.
- Ouvrir xbar, Raycast, Clipy et CodexBar. Activer leur lancement au démarrage depuis leurs réglages et accorder les autorisations macOS nécessaires.
- Dans xbar : Refresh all. Vérifier visuellement ✅, 🍊 ou 🚨 et ouvrir une PR s'il y en a. Les filtres conservent le comportement du script d'origine : PR ouvertes, review demandée à l'utilisateur connecté, hors drafts et `review:none`.
- Configurer la connexion/provider dans CodexBar.
- Ouvrir Docker et terminer sa configuration. Vérifier `docker info` une fois démarré.
- Agenda : utilisé dans Raycast, déjà inclus dans le Brewfile essentiel. Sur le nouveau Mac, restaurer les réglages Raycast, reconnecter les comptes calendrier nécessaires et accorder les autorisations demandées. Vérifier que l'agenda affiche les événements attendus. Les comptes, calendriers sélectionnés et raccourcis restent à récupérer ; aucune donnée de calendrier n'est versionnée.

## Réglages et exports à récupérer sur l'ancien Mac

- Suivre [restore.md](restore.md) pour le contenu capturé et l'ordre exact de restauration. La sauvegarde privée doit être transférée hors de l'ancien Mac.
- Raycast : exporter les réglages via l'interface dans un `.rayconfig` privé chiffré. Sur le nouveau Mac, importer puis reconnecter les extensions. Agenda : commande My Schedule de Calendar.
- Firefox : activer la synchronisation souhaitée. JetBrains : reprendre les keymaps/options privées capturées ou utiliser Settings Sync, puis réinstaller les plugins.
- Clipy : les raccourcis sont capturés dans les préférences sélectionnées ; aucun historique du presse-papiers n'est transféré.
- Codex : les skills personnels sont dans la sauvegarde privée. Réinstaller les plugins et reconnecter les MCP selon l'inventaire privé ; aucune session, mémoire ni authentification n'est copiée.
- Terminal, Dock, Clipy et CodexBar : préférences sélectionnées dans `configs/preferences`. Les permissions macOS et les comptes restent à rétablir humainement.

## Développement et logiciels plus lourds

- Les versions Node/Go/PHP et dépendances se déterminent depuis chaque projet. `nvm` et `mise` sont installés, mais aucun Node par défaut arbitraire n'est imposé. Installer les versions demandées avant de lancer les projets.
- Cloner les projets voulus sous `~/Desktop/gdc/` si l'on conserve les chemins actuels. Le monorepo infra contient ses propres AGENTS.md ; suivre les README/Makefile par service. Aucun clone professionnel ni secret d'environnement n'est inclus dans le bootstrap public.
- S'authentifier aux services AWS/VPN et aux registries selon les procédures de l'entreprise. Certificats locaux via `mkcert -install` uniquement si un projet en a besoin.
- Xcode : installer les versions exigées via Xcodes, terminer licence et composants depuis l'interface. Les Command Line Tools ne remplacent pas Xcode complet.
- Adobe Acrobat/InDesign/Creative Cloud, Numbers, HiSuite, Malwarebytes et l'app Focus To-Do/WebPomodoro ont été repérés ou utilisés mais restent à installer/configurer manuellement si utiles. Ne pas recopier leurs licences ou leurs sessions.
- Redis/MySQL serveurs et anciennes versions Go étaient installés ; les besoins et données sont propres aux projets. Ne pas démarrer un service ni transférer une base automatiquement. Les clients sont dans les extras.

## Validation opérationnelle

`verify.sh` contrôle installation, configs et accès PR. Il ne prouve pas que les apps sont connectées, qu'un calendrier s'affiche, qu'un VPN fonctionne ou qu'un projet démarre.

Avant de conclure : vérifier visuellement les apps de barre de menu et l'agenda Raycast, accéder à GitHub et aux outils de travail, puis lancer au moins un projet utile avec ses dépendances. Signaler explicitement les étapes manquantes, notamment les réglages et exports non capturés.
