#!/usr/bin/env python3
"""xbar PR reviews, inspired by Adam Bogdał's Github review requests plugin.

Authentication uses gh's local credential store; no token is saved here.
"""
# <xbar.title>GitHub review requests</xbar.title>
# <xbar.desc>Open review requests for the authenticated GitHub user</xbar.desc>
# <xbar.dependencies>python3,gh</xbar.dependencies>

import json
import shutil
import subprocess
import sys
from pathlib import Path

QUERY = """
query($searchQuery: String!) {
  search(query: $searchQuery, type: ISSUE, first: 100) {
    issueCount
    nodes {
      ... on PullRequest {
        repository { nameWithOwner }
        author { login }
        number
        url
        title
      }
    }
  }
}
"""


def gh_path():
    executable = shutil.which("gh")
    if executable:
        return executable
    for path in ("/opt/homebrew/bin/gh", "/usr/local/bin/gh"):
        if Path(path).is_file():
            return path
    raise RuntimeError("Installer gh puis lancer gh auth login")


def api(executable, *arguments):
    result = subprocess.run(
        [executable, "api", "--hostname", "github.com", *arguments],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode:
        # Do not forward stderr: keep credentials and private error details local.
        raise RuntimeError("Accès GitHub impossible : vérifier gh auth status et le réseau")
    return result.stdout


def fetch_reviews():
    executable = gh_path()
    login = json.loads(api(executable, "user"))["login"]
    search = f"type:pr state:open review-requested:{login} draft:false review:none"
    response = json.loads(api(executable, "graphql", "-f", f"query={QUERY}",
                              "-f", f"searchQuery={search}"))
    if response.get("errors"):
        raise RuntimeError("Recherche GitHub en erreur ; vérifier les accès")
    return response["data"]["search"]


def menu_text(value):
    return str(value).replace("|", "｜").replace("\n", " ").replace("\r", " ")


def main():
    check_only = sys.argv[1:] == ["--check"]
    if sys.argv[1:] and not check_only:
        print("Usage: pr.5m.py [--check]", file=sys.stderr)
        return 1
    try:
        reviews = fetch_reviews()
        count = reviews["issueCount"]
    except (RuntimeError, subprocess.TimeoutExpired, OSError, ValueError, KeyError, TypeError):
        message = "Vérifier gh auth login, les accès GitHub et le réseau"
        if check_only:
            print(message, file=sys.stderr)
            return 1
        print("⚠️ PR\n---\n" + message)
        return 0
    if check_only:
        print(f"GitHub OK : {count} PR")
        return 0
    print("✅" if count == 0 else f"{'🚨' if count > 5 else '🍊'} {count}")
    print("---")
    for pr in reviews["nodes"]:
        title = menu_text(f"{pr['repository']['nameWithOwner']} - {pr['title']}")
        print(f"{title} | href={pr['url']}")
        author = (pr.get("author") or {}).get("login", "compte supprimé")
        print(f"#{pr['number']} par @{menu_text(author)} | size=12")
        print("---")
    if count > len(reviews["nodes"]):
        print("100 premières PR affichées ; consulter GitHub pour la suite")
    print("Reviews sur GitHub | href=https://github.com/pulls/review-requested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
