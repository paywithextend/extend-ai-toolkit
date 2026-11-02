"""Check public version-specific PyPI advisories; never execute downloaded code."""
import importlib.metadata
import json
import urllib.error
import urllib.request

# Packaging bootstrap tools are not part of the package's installed runtime graph.
BOOTSTRAP = {"pip", "setuptools", "wheel"}
failures = []

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
        failures.append(entry)
print(json.dumps({"active_advisories": failures}, indent=2))
raise SystemExit(bool(failures))
