# Chargé depuis ~/.zshrc ; ne contient aucun secret.
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)
if [[ -f "$ZSH/oh-my-zsh.sh" ]] && ! typeset -f omz >/dev/null; then
  source "$ZSH/oh-my-zsh.sh"
fi

alias gs='git status'
alias ga='git add'
alias gp='git push'
alias gcm='git commit -m'
alias gco='git checkout'
alias gr='git rebase -i'

export NVM_DIR="$HOME/.nvm"
if command -v brew >/dev/null 2>&1; then
  setup_brew_prefix="$(brew --prefix)"
  [[ ! -s "$setup_brew_prefix/opt/nvm/nvm.sh" ]] || source "$setup_brew_prefix/opt/nvm/nvm.sh"
  unset setup_brew_prefix
fi
typeset -U path
path+=("$HOME/.local/bin" "$HOME/Library/Application Support/JetBrains/Toolbox/scripts")
autoload -Uz compinit
[[ ! -d "$HOME/.zfunc" ]] || fpath+=("$HOME/.zfunc")
compinit
zstyle ':completion:*' menu select
