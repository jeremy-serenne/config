#!/bin/bash
set -uo pipefail
[[ "$(uname -s)" == Darwin ]] || { echo 'Setup disponible uniquement pour macOS.' >&2; exit 1; }
repo="$(cd "$(dirname "$0")/.." && pwd)"
case "${1:-}" in '') extras=false ;; --extras) extras=true ;; *) echo 'Usage: bash macos/verify.sh [--extras]'; exit 1 ;; esac
[[ $# -le 1 ]] || exit 1
for candidate in /opt/homebrew/bin/brew /usr/local/bin/brew; do
  if [[ -x "$candidate" ]]; then eval "$("$candidate" shellenv)"; break; fi
done
failed=0
check() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "OK : $label"; else echo "À FAIRE : $label"; failed=1; fi
}
check 'Homebrew et apps essentielles' brew bundle check --file="$repo/macos/Brewfile"
if $extras; then check 'Apps et outils supplémentaires' brew bundle check --file="$repo/macos/Brewfile.extras"; fi
check 'Command Line Tools' xcode-select -p
check 'GitHub connecté' gh auth status --hostname github.com
check 'Email Git réel' bash -c 'email=$(git config user.email); [[ -n "$email" && "$email" != mail@mail.com ]]'
check 'Nom Git défini' git config user.name
for name in gitconfig zshrc.zsh; do
  check "Config $name à jour" cmp -s "$repo/macos/configs/$name" "$HOME/.config/jeremy-setup/$name"
done
check 'Config Git chargée' bash -c 'git config --global --get-all include.path | grep -Fqx "$HOME/.config/jeremy-setup/gitconfig"'
check 'Config shell chargée' grep -Fq 'source "$HOME/.config/jeremy-setup/zshrc.zsh"' "$HOME/.zshrc"
check 'Oh My Zsh' test -f "$HOME/.oh-my-zsh/oh-my-zsh.sh"
check 'Plugin xbar à jour' cmp -s "$repo/macos/xbar/pr.5m.py" "$HOME/Library/Application Support/xbar/plugins/pr.5m.py"
check 'Plugin exécutable' test -x "$HOME/Library/Application Support/xbar/plugins/pr.5m.py"
check 'Pas de doublon ancien pr.py' test ! -e "$HOME/Library/Application Support/xbar/plugins/pr.py"
check 'Recherche PR GitHub fonctionnelle' python3 "$repo/macos/xbar/pr.5m.py" --check
echo 'À vérifier humainement : barre de menu, agenda, connexions, Docker et lancement d’un projet. Voir manual-steps.md.'
exit "$failed"
