#!/usr/bin/env python3
"""Preview or apply selected preferences, preserving unrelated keys."""
import argparse
import plistlib
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if sys.platform != 'darwin': parser.error('macOS only')
    paths = sorted(args.directory.glob('*.plist'))
    if not paths: parser.error('No preference plists found')
    for path in paths:
        desired = plistlib.loads(path.read_bytes())
        domain = path.stem
        print(('APPLY' if args.apply else 'WOULD APPLY'), domain, ', '.join(desired))
        if not args.apply: continue
        current = subprocess.run(['defaults', 'export', domain, '-'], capture_output=True)
        data = plistlib.loads(current.stdout) if current.returncode == 0 else {}
        if domain == 'com.apple.Terminal':
            # Preserve profile settings such as startup commands not captured here.
            profiles = data.setdefault('Window Settings', {})
            for name, settings in desired.get('Window Settings', {}).items():
                profiles.setdefault(name, {}).update(settings)
            desired = {k: v for k, v in desired.items() if k != 'Window Settings'}
        data.update(desired)
        with tempfile.NamedTemporaryFile(suffix='.plist') as temporary:
            temporary.write(plistlib.dumps(data)); temporary.flush()
            subprocess.run(['defaults', 'import', domain, temporary.name], check=True)
    print('Reopen the affected apps to check appearance and shortcuts. No app was restarted.')


if __name__ == '__main__': main()
