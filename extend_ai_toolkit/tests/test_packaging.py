from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib  # type: ignore[import-not-found]


def _pyproject():
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    return tomllib.loads(path.read_text())


def test_base_install_excludes_framework_runtime_dependencies():
    dependencies = _pyproject()["project"]["dependencies"]

    assert "paywithextend==2.0.0" in dependencies
    assert not any(
        dependency.startswith(
            (
                "langchain",
                "openai",
                "openai-agents",
                "mcp",
                "crewai",
                "starlette",
            )
        )
        for dependency in dependencies
    )


def test_framework_dependencies_are_available_as_extras():
    extras = _pyproject()["project"]["optional-dependencies"]

    assert any(dependency.startswith("langchain") for dependency in extras["langchain"])
    assert any(dependency.startswith("mcp") for dependency in extras["mcp"])
    assert any(dependency.startswith("openai-agents") for dependency in extras["openai"])
    assert any(dependency.startswith("crewai") for dependency in extras["crewai"])
