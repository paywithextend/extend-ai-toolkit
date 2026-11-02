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
   The workflow reserves the version tag at the merged commit before uploading,
   verifies any existing PyPI files match the approved artifacts, and publishes
   through OIDC. It verifies the complete file set before creating the GitHub release.
5. Confirm both distributions exist on PyPI and a fresh installation reports the
   expected version. For a failed run, use **Re-run failed jobs** on the original
   run: it reuses that run's commit and built distributions. Never move the version
   tag or delete it to retry publication. A new run at a later commit with the same
   version is rejected, even if a GitHub release has not yet been created.
   Manual dispatch is only suitable while `main` still points to the original
   commit; rebuilt files must match any existing PyPI file hashes. If they differ,
   recover using the original run's artifacts, or prepare a new package version.
6. Merge release-only metadata changes back into `development` when necessary.

Publish SDK 3.0.0 before toolkit 2.0.0, which requires `paywithextend==3.0.0`.
A successful offline test run does not establish live endpoint availability or
account permissions. See the availability notes in the README.
