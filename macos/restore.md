# Restaurer le setup capturé

À lire sur un nouveau Mac ou avant une nouvelle capture. Le dépôt public et la sauvegarde privée sont complémentaires.

## Dépôt public

- `Brewfile` et `Brewfile.extras` installent les apps/outils.
- `configs/` contient Git/zsh et les préférences sélectionnées : profils Terminal (polices/couleurs), raccourcis Clipy, Dock, extensions de fichiers et affichage CodexBar. Aucun historique ou compte n'est inclus.
- `current-tools.json` conserve les versions observées le 6 octobre 2026 ; ce n'est pas un verrou de versions. Node installé sur le Mac capturé : v24.19.0. Les projets gardent priorité pour leurs versions d'exécution.

## Sauvegarde privée

Capture initiale locale : `~/Documents/Mac-setup-backup/2026-10-06/`. Copier ce dossier vers un stockage privé indépendant avant de changer de Mac. Une copie locale seule ne protège pas de la perte de la machine.

La capture `snapshot/` contient :

- Shell/Git personnels filtrés ; identité Git et chemins propres à l'utilisateur restent privés.
- Skills personnels Codex/agents et customisations Oh My Zsh, hors caches et liens vers les plugins fournis.
- Derniers dossiers de réglages JetBrains de chaque produit : options sélectionnées, keymaps, couleurs, styles et templates. Sources de données, comptes, licences et fichiers récents sont exclus.
- Préférences sélectionnées et inventaire privé Codex/MCP/plugins/outils. L'inventaire Codex retire env, headers, tokens et politiques de sécurité ; il sert à reconstruire les connexions, pas à contourner une authentification.
- `manifest.json` : fichiers, empreintes SHA-256 et exclusions. Inspecter les exclusions avant de promettre une restauration complète.

Les sessions, clés privées, credentials, licences, historiques et bases de données ne sont pas sauvegardés. Les fichiers contenant un secret détecté sont exclus ; les lignes de shell correspondantes sont omises. Ce filtre n'est pas un audit de sécurité exhaustif : conserver tout le dossier en privé, ne jamais le committer.

Raycast utilise séparément son export natif chiffré `.rayconfig`. Inclure Settings, Extensions, Quicklinks, catégories Focus, Script Directories et Snippets ; exclure Clipboard History, AI Chats et Notes pour une sauvegarde du setup. Ne pas recopier sa base SQLite chiffrée : l'export natif est le format de transfert. Conserver le mot de passe de l'export dans Bitwarden, séparément du fichier.

## Ordre de restauration pour l'agent

1. Récupérer le dépôt et la sauvegarde privée. Installer les Command Line Tools et Homebrew selon `AGENTS.md`. Utiliser le Python Homebrew (`brew install python`) avant `backup.py`, qui nécessite Python 3.11 ou supérieur.
2. Avant le bootstrap, prévisualiser les fichiers personnels :

   ```sh
   python3 macos/backup.py restore /chemin/prive/snapshot
   python3 macos/backup.py restore /chemin/prive/snapshot --apply
   ```

   Le deuxième appel ne restaure que les fichiers absents ; les conflits restent intacts et le programme renvoie 1. Examiner les différences pour fusionner. Aucune politique Codex ni permission macOS n'est appliquée.
3. Lancer le bootstrap essentiel, puis les extras. Vérifier l'inventaire Node privé et installer v24.19.0 via nvm si l'on souhaite retrouver le runtime actuel ; suivre ensuite les versions exigées par chaque projet.
4. Restaurer les préférences sélectionnées après avoir fermé les apps concernées :

   ```sh
   python3 macos/preferences.py macos/configs/preferences
   python3 macos/preferences.py macos/configs/preferences --apply
   ```

   La première commande prévisualise. La seconde fusionne les clés capturées avec les préférences présentes ; elle ne supprime pas les autres clés et ne relance pas les apps. Préserver les éventuels réglages souhaités sur une machine déjà utilisée.
5. Raycast : lancer **Import Settings & Data**, choisir le `.rayconfig` privé et laisser l'utilisateur saisir le mot de passe. Reconnecter les comptes/extensions nécessaires. Agenda : commande **My Schedule** de Calendar ; vérifier les événements et les calendriers sélectionnés.
6. JetBrains : installer le produit avant de reprendre ses réglages, avec l'IDE fermé. Les snapshots portent la version d'origine ; si la version installée diffère, comparer/migrer les options vers son dossier réel au lieu de créer uniquement un dossier d'ancienne version. Réinstaller les plugins via JetBrains/Settings Sync et reconnecter la licence.
7. Codex : les skills personnels sont restaurés dans leur emplacement d'origine. Les skills/plugins fournis par des plugins ne sont pas copiés ; les réinstaller depuis leurs sources. Reconstruire la config locale avec `inventory.json`, adapter les chemins (nom d'utilisateur, repo, runtimes), puis reconnecter les MCP. Ne pas appliquer automatiquement les anciennes règles de confiance/permissions.
8. Contrôler `verify.sh`, le menu xbar, les raccourcis du terminal, Raycast/My Schedule, Clipy et un projet réel. Nommer toute connexion ou export encore manquant.

## Actualiser la sauvegarde

```sh
python3 macos/backup.py capture /chemin/prive/nouvelle-capture
```

La destination doit être nouvelle. Aucune sauvegarde existante n'est écrasée. Renouveler aussi l'export Raycast après un changement important.

Sources : [export/import Raycast](https://www.raycast.com/changelog/1-22-0), [réglages JetBrains](https://www.jetbrains.com/help/rider/Sharing_Your_IDE_Settings.html).
