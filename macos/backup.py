#!/usr/bin/env python3
"""Capture/restore selected personal settings locally. Never commit the backup."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import tomllib
from urllib.parse import urlsplit, urlunsplit

SECRET = re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN .*PRIVATE KEY|(?i:)(?:sk-[A-Za-z0-9_-]{20,})')
SENSITIVE_LINE = re.compile(r'(?i)(?:token|password|secret|api[_-]?key|authorization|credential)\s*[=:]')
PREFS = {
    'com.apple.dock': ['autohide', 'orientation', 'tilesize', 'magnification', 'largesize', 'show-recents', 'minimize-to-application', 'wvous-br-corner', 'wvous-bl-corner', 'wvous-tr-corner', 'wvous-tl-corner'],
    'NSGlobalDomain': ['AppleInterfaceStyle', 'AppleShowAllExtensions', 'KeyRepeat', 'InitialKeyRepeat', 'NSAutomaticSpellingCorrectionEnabled', 'NSAutomaticQuoteSubstitutionEnabled', 'NSAutomaticDashSubstitutionEnabled', 'AppleKeyboardUIMode'],
    'com.clipy-app.Clipy': ['loginItem', 'kCPYHotKeySnippetKeyCombo', 'kCPYHotKeyMainKeyCombo', 'kCPYHotKeyHistoryKeyCombo'],
    'com.steipete.codexbar': ['refreshFrequency', 'launchAtLogin', 'menuBarMetricPreferences', 'costSummaryDisplayStyle', 'tokenCostUsageEnabled'],
}


def safe_config(value):
    if isinstance(value, dict):
        return {k: safe_config(v) for k, v in value.items() if not re.search(r'(?i)(token|password|secret|credential|header|^env$|trust|permission|approval|sandbox)', k)}
    if isinstance(value, list):
        if any(isinstance(v, str) and re.search(r'(?i)(token|password|secret|api.key|bearer)', v) for v in value): return []
        return [safe_config(v) for v in value]
    if isinstance(value, str):
        if SECRET.search(value): return '[omitted]'
        if value.startswith(('https://', 'http://')):
            url = urlsplit(value)
            return urlunsplit((url.scheme, url.netloc.split('@')[-1], url.path, '', ''))
    return value


def file_candidates(home):
    for name in ('.zshrc', '.zprofile', '.bashrc', '.bash_profile', '.gitconfig', '.gitignore_global', '.tool-versions', '.nvm/alias/default', '.codex/AGENTS.md', '.codex/RTK.md'):
        yield home / name
    for relative in ('.codex/skills', '.agents/skills', '.oh-my-zsh/custom'):
        base = home / relative
        if base.exists():
            for directory, dirs, files in os.walk(base, followlinks=False):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.venv', 'venv', 'cache') and not Path(directory, d).is_symlink()]
                yield from (Path(directory) / name for name in files)
    jb = home / 'Library/Application Support/JetBrains'
    if jb.exists():
        products = {}
        for base in sorted(jb.iterdir()):
            match = re.match(r'(GoLand|WebStorm|IntelliJIdea|RustRover)(\d.*)', base.name)
            if match:
                products[match[1]] = base
        for base in products.values():
            for folder in ('options', 'keymaps', 'codestyles', 'colors', 'templates'):
                if (base / folder).exists():
                    yield from (base / folder).rglob('*.xml')
            yield base / 'disabled_plugins.txt'


def capture(home, backup):
    backup.mkdir(parents=True, exist_ok=False, mode=0o700)
    copied, skipped = [], []
    for source in file_candidates(home):
        if not source.is_file() or source.is_symlink():
            continue
        relative = source.relative_to(home)
        if source.name.startswith('.env') or source.suffix in ('.pem', '.key', '.p12') or re.search(r'(?i)(auth|credential|password|license|datasource|recent|workspace|statistics|usage|account|github|ssh|http)', source.name):
            skipped.append(str(relative)); continue
        try:
            content = source.read_text()
        except (UnicodeError, OSError):
            skipped.append(str(relative)); continue
        if SECRET.search(content):
            # Preserve shell settings while dropping lines containing credentials.
            if source.name in ('.zshrc', '.zprofile', '.bashrc', '.bash_profile'):
                content = '\n'.join(line for line in content.splitlines() if not SECRET.search(line) and not SENSITIVE_LINE.search(line)) + '\n'
            else:
                skipped.append(str(relative)); continue
        content = '\n'.join(line for line in content.splitlines() if not SENSITIVE_LINE.search(line)) + '\n' if source.name.startswith(('.zsh', '.bash')) else content
        target = backup / 'files' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        target.chmod(0o700 if source.stat().st_mode & 0o111 else 0o600)
        copied.append(str(relative))
    preferences = {}
    for domain, keys in PREFS.items():
        result = subprocess.run(['defaults', 'export', domain, '-'], capture_output=True)
        if result.returncode == 0:
            data = plistlib.loads(result.stdout)
            preferences[domain] = {k: data[k] for k in keys if k in data}
    # Terminal profiles include binary font/color values: keep their plist format.
    result = subprocess.run(['defaults', 'export', 'com.apple.Terminal', '-'], capture_output=True)
    if result.returncode == 0:
        data = plistlib.loads(result.stdout)
        profiles = data.get('Window Settings', {})
        safe_keys = {'name', 'type', 'Font', 'FontAntialias', 'TextColor', 'BackgroundColor', 'CursorColor', 'CursorType', 'columnCount', 'rowCount', 'UseBoldFonts', 'UseBrightBold', 'FontWidthSpacing', 'FontHeightSpacing', 'BackgroundAlpha'}
        preferences['com.apple.Terminal'] = {k: data[k] for k in ('Default Window Settings', 'Startup Window Settings') if k in data}
        preferences['com.apple.Terminal']['Window Settings'] = {name: {k: v for k, v in settings.items() if k in safe_keys} for name, settings in profiles.items()}
    for domain, data in preferences.items():
        target = backup / 'preferences' / (domain + '.plist')
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(plistlib.dumps(data)); target.chmod(0o600)
    codex_file = home / '.codex/config.toml'
    codex = tomllib.loads(codex_file.read_text()) if codex_file.exists() else {}
    inventory = {'codex': safe_config({key: codex[key] for key in ('model', 'model_reasoning_effort', 'personality', 'service_tier', 'mcp_servers', 'plugins', 'marketplaces', 'skills', 'desktop') if key in codex}), 'mcp_servers': list(codex.get('mcp_servers', {})), 'plugins': list(codex.get('plugins', {})), 'node_versions': [p.name for p in (home / '.nvm/versions/node').glob('*')], 'preferences': list(preferences)}
    for label, args in {'formulae': ['brew', 'list', '--formula', '--versions'], 'casks': ['brew', 'list', '--cask', '--versions'], 'npm_global': ['npm', 'list', '-g', '--depth=0', '--json']}.items():
        if shutil.which(args[0]):
            result = subprocess.run(args, capture_output=True, text=True, env={**os.environ, 'HOMEBREW_NO_AUTO_UPDATE': '1'}, timeout=60)
            if result.returncode == 0 and not SECRET.search(result.stdout): inventory[label] = result.stdout
    (backup / 'inventory.json').write_text(json.dumps(inventory, indent=2))
    hashes = {str(p.relative_to(backup)): hashlib.sha256(p.read_bytes()).hexdigest() for p in backup.rglob('*') if p.is_file()}
    (backup / 'manifest.json').write_text(json.dumps({'files': hashes, 'copied': copied, 'excluded': skipped, 'raycast': 'Export Settings & Data required separately'}, indent=2))
    print(f'Captured {len(copied)} files and {len(preferences)} preference domains in {backup}')
    print(f'{len(skipped)} files excluded; see local manifest.json. No sessions or credentials copied.')


def restore(home, backup, apply):
    manifest = json.loads((backup / 'manifest.json').read_text())
    for relative, digest in manifest['files'].items():
        source = backup / relative
        if not source.resolve().is_relative_to(backup.resolve()) or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError('Backup integrity failure')
    conflicts = 0
    for relative in manifest['copied']:
        source, target = backup / 'files' / relative, home / relative
        if not source.resolve().is_relative_to((backup / 'files').resolve()) or not target.resolve().is_relative_to(home.resolve()):
            raise ValueError('Unsafe backup path')
        if target.exists() or target.is_symlink():
            if target.is_file() and target.read_bytes() == source.read_bytes(): continue
            print('CONFLICT (kept):', relative); conflicts += 1
        else:
            print('RESTORE' if apply else 'WOULD RESTORE', relative)
            if apply:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    print('Import selected preferences and Raycast through the documented procedure; do not replace entire domains.')
    return 1 if conflicts else 0


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['capture', 'restore'])
    parser.add_argument('directory', type=Path)
    parser.add_argument('--apply', action='store_true', help='Restore missing files; otherwise preview only')
    args = parser.parse_args()
    if sys.platform != 'darwin': parser.error('macOS only')
    if args.mode == 'capture':
        if args.apply: parser.error('--apply is only valid for restore')
        capture(Path.home(), args.directory.expanduser().resolve())
        return 0
    return restore(Path.home(), args.directory.expanduser().resolve(), args.apply)


if __name__ == '__main__':
    sys.exit(main())
