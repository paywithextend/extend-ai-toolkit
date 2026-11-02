# Publishing a release

Releases promote reviewed changes to `main`. Merging a release PR automatically
starts validation and building. Publication waits for approval of the `pypi`
environment.

## One-time publisher configuration

1. Create the GitHub environment `pypi` and restrict deployment branches to `main`.
   Configure the repository's required release reviewers before publishing.
2. On PyPI, configure a Trusted Publisher for the existing `extend-ai-toolkit` project:
   owner `paywithextend`, repository `extend-ai-toolkit`, workflow `release.yml`,
   environment `pypi`.
3. Verify both configurations before releasing. The workflow uses GitHub OIDC;
   the legacy `PYPI_API_TOKEN` secret is not used. Do not remove legacy credentials
   until the replacement publisher has been verified.

## Release procedure

1. Update `extend_ai_toolkit/__version__.py`, the changelog and migration notes together
   in a PR to `development`. Merge after review and successful CI.
2. Open a release PR to `main`; require review and successful Python 3.11–3.13 CI.
3. Merge the release PR. **Publish reviewed toolkit** starts automatically on `main`,
   reads the version from that exact commit, and skips versions with an existing
   GitHub release. Never reuse a published version or move its tag.
4. After source tests, installed-wheel import checks and runtime advisory checks pass,
   an authorized reviewer approves the `pypi` deployment in the Actions run.
   GitHub publishes the validated artifacts through OIDC, then creates the version
   tag and GitHub release at the merged commit using the changelog as release notes.
5. Confirm both distributions exist on PyPI and a fresh installation reports the
   expected version. For a failed run, use **Re-run failed jobs**. Publication skips
   existing files so a partial upload or GitHub release failure can be recovered
   without replacing published files. **Run workflow** on `main` remains available
   for recovery; no tag input or manual tag creation is needed.
6. Merge release-only metadata changes back into `development` when necessary.

Publish SDK 3.0.0 before toolkit 2.0.0, which requires `paywithextend==3.0.0`.
A successful offline test run does not establish live endpoint availability or
account permissions. See the availability notes in the README.
