#!/bin/bash
set -euo pipefail

[[ "$(uname -s)" == Darwin ]] || { echo 'Setup disponible uniquement pour macOS.' >&2; exit 1; }
extras=false
case "${1:-}" in
  '') ;;
  --extras) extras=true ;;
  *) echo 'Usage: bash macos/bootstrap.sh [--extras]' >&2; exit 1 ;;
esac
[[ $# -le 1 ]] || exit 1
repo="$(cd "$(dirname "$0")/.." && pwd)"
command -v brew >/dev/null 2>&1 || {
  for candidate in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [[ -x "$candidate" ]]; then eval "$("$candidate" shellenv)"; break; fi
  done
}
command -v brew >/dev/null 2>&1 || { echo 'Installer Homebrew depuis https://brew.sh puis relancer.' >&2; exit 1; }
xcode-select -p >/dev/null 2>&1 || { echo 'Terminer xcode-select --install puis relancer.' >&2; exit 1; }

brew bundle install --file="$repo/macos/Brewfile" --no-upgrade
if $extras; then brew bundle install --file="$repo/macos/Brewfile.extras" --no-upgrade; fi

conflicts=0
install_config() {
  local source="$1" target="$2"
  if [[ -e "$target" || -L "$target" ]]; then
    if ! cmp -s "$source" "$target"; then
      echo "CONFLIT : conservé $target ; comparer avec $source" >&2
      conflicts=$((conflicts + 1))
    fi
  else
    mkdir -p "$(dirname "$target")"
    cp "$source" "$target"
  fi
}
append_once() {
  local target="$1" line="$2"
  touch "$target"
  if ! grep -Fqx "$line" "$target"; then printf '\n%s\n' "$line" >> "$target"; fi
}

config_dir="$HOME/.config/jeremy-setup"
install_config "$repo/macos/configs/gitconfig" "$config_dir/gitconfig"
install_config "$repo/macos/configs/zshrc.zsh" "$config_dir/zshrc.zsh"
install_config "$repo/macos/xbar/pr.5m.py" "$HOME/Library/Application Support/xbar/plugins/pr.5m.py"
if cmp -s "$repo/macos/xbar/pr.5m.py" "$HOME/Library/Application Support/xbar/plugins/pr.5m.py"; then
  chmod +x "$HOME/Library/Application Support/xbar/plugins/pr.5m.py"
fi
if [[ -e "$HOME/Library/Application Support/xbar/plugins/pr.py" ]]; then
  echo 'CONFLIT : ancien pr.py présent ; comparer avant de désactiver le doublon.' >&2
  conflicts=$((conflicts + 1))
fi

if ! git config --global --get-all include.path | grep -Fqx "$config_dir/gitconfig"; then
  git config --global --add include.path "$config_dir/gitconfig"
fi
brew_prefix="$(brew --prefix)"
append_once "$HOME/.zprofile" "eval \"\$(\"$brew_prefix/bin/brew\" shellenv)\""
append_once "$HOME/.zshrc" '[[ ! -f "$HOME/.config/jeremy-setup/zshrc.zsh" ]] || source "$HOME/.config/jeremy-setup/zshrc.zsh"'
mkdir -p "$HOME/.nvm"
if [[ ! -e "$HOME/.oh-my-zsh" ]]; then
  git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git "$HOME/.oh-my-zsh"
fi

echo 'Installation terminée. Connexions et vérifications : macos/manual-steps.md.'
if [[ "$conflicts" -gt 0 ]]; then echo "$conflicts conflit(s) à résoudre." >&2; exit 1; fi
