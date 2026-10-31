"""Check public version-specific PyPI advisories; never execute downloaded code."""
import importlib.metadata
import json
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# Packaging bootstrap tools are not part of the package's installed runtime graph.
BOOTSTRAP = {"pip", "setuptools", "wheel"}
failures = []
reviewed = []
exceptions = json.loads(Path(__file__).with_name("advisory-dispositions.json").read_text())

for distribution in sorted(importlib.metadata.distributions(), key=lambda d: d.metadata["Name"]):
    name = distribution.metadata["Name"]
    if name.lower() in BOOTSTRAP:
        continue
    url = f"https://pypi.org/pypi/{name}/{distribution.version}/json"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            metadata = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and name.lower() in {"paywithextend", "extend-ai-toolkit", "extend_ai_toolkit"}:
            continue  # Unpublished local wheel under review.
        raise
    active = [v["id"] for v in metadata.get("vulnerabilities", []) if not v.get("withdrawn")]
    if active:
        entry = {"package": name, "version": distribution.version, "advisories": active}
        disposition = exceptions.get(f"{name.lower()}=={distribution.version}")
        if (disposition and date.today() <= date.fromisoformat(disposition["review_by"])
                and set(active) <= set(disposition["advisories"])):
            reviewed.append({**entry, "disposition": disposition["reason"], "review_by": disposition["review_by"]})
        else:
            failures.append(entry)
print(json.dumps({"unreviewed_advisories": failures, "reviewed_advisories": reviewed}, indent=2))
raise SystemExit(bool(failures))
