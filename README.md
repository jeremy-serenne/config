# Mon setup

Objectif : retrouver rapidement un Mac opérationnel, avec l'aide d'un agent.

## Nouveau Mac

1. Installer Codex depuis sa source officielle et se connecter.
2. Récupérer ce dépôt. Sans Git, télécharger l'archive depuis GitHub ; sinon :

   ```sh
   git clone https://github.com/jeremy-serenne/config.git ~/config
   ```

3. Ouvrir ce dossier dans Codex et demander :

   > Configure ce Mac en suivant AGENTS.md. Installe d'abord le setup essentiel, vérifie-le et guide-moi pour les étapes humaines restantes. Puis installe les apps supplémentaires.

L'agent suit [la procédure macOS](macos/AGENTS.md). Linux n'est pas encore pris en charge.

## Installation directe

Après installation de Homebrew et des Command Line Tools :

```sh
bash macos/bootstrap.sh
bash macos/verify.sh
# Apps et outils secondaires, ensuite :
bash macos/bootstrap.sh --extras
bash macos/verify.sh --extras
```

L'installation conserve les fichiers existants différents et signale les conflits. Elle n'installe pas de secrets, ne supprime pas de logiciels et ne met pas à jour les packages déjà présents.

## Ce qui est enregistré

- Apps et outils : [Brewfile](macos/Brewfile), [extras](macos/Brewfile.extras).
- Git, shell zsh et plugin xbar de reviews GitHub.
- Connexions, démarrage automatique, agenda, exports d'apps et projets : [étapes manuelles](macos/manual-steps.md).
- Réglages capturés et sauvegarde privée : [procédure de restauration](macos/restore.md). À transférer hors de l'ancien Mac avant de le remplacer.

Inventaire initial : 5 octobre 2026. Les manifestes décrivent les logiciels à installer, pas des versions figées ni une sauvegarde complète du Mac.

Le `.gitconfig` racine est conservé comme ancien modèle. Le setup utilise `macos/configs/gitconfig`, sans identité Git fictive ; définir son email localement.
