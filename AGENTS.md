# API4Jenkins Agent Guide

Python client library for the Jenkins API with sync and async APIs.

## Essential Commands

```bash
# Default gate: style -> lint -> unit tests
tox

# Run only unit tests (uses mocked Jenkins responses)
tox -e py3

# Run only style or lint
tox -e style
tox -e lint

# Integration tests (require a live Jenkins instance)
tox -e integration
```

**No `pyproject.toml`** — this is a pure setuptools project. `setup.py` has **no `[dev]` extras**, so do not use `pip install -e .[dev]`. Install dev dependencies via the tox environments or manually (`respx`, `pytest-cov`, `pytest-asyncio`, `ruff`, `pycodestyle`).

## Repository Layout

- `api4jenkins/` — Main package
  - Entry points: `Jenkins` and `AsyncJenkins` in `__init__.py`
  - Core: `item.py`, `job.py`, `build.py`, `http.py`
  - Components: `credential.py`, `node.py`, `plugin.py`, `queue.py`, `view.py`, `system.py`, `user.py`
  - Utilities: `mix.py`, `mixins.py`, `exceptions.py`, `__version__.py`
- `tests/unit/` — Mocked unit tests with JSON fixtures in `tests_data/`
- `tests/integration/` — Live Jenkins tests with session-scoped fixture setup
- `run.py` — **Developer scratchpad** with hardcoded URLs/credentials; not an example script

## Code Patterns

- **Sync/async pairs**: Every class has a sync variant (e.g., `Item`, `Jenkins`) and an async variant prefixed with `Async` (e.g., `AsyncItem`, `AsyncJenkins`). Keep methods symmetric when adding features.
- **Dynamic class loading**: Jenkins returns `_class` in JSON; `new_item()` maps it to a local class name. If a class is missing, the library raises `AttributeError` and suggests patching with `api4jenkins._patch_to()`.
- **Dynamic attributes**: Item objects expose Jenkins JSON fields via `__getattr__` (e.g., `job.display_name`). For async items, this requires `await`.
- **Async properties are actually coroutines**: In async classes, `await client.version`, `await item.exists()`, and `await item.dynamic_attrs` all require awaiting.
- **HTTP layer**: All requests go through `httpx` clients created in `http.py` with event hooks for logging and automatic error translation (`404 -> ItemNotFoundError`, `401 -> AuthenticationError`, `403 -> PermissionError`, `400 -> BadRequestError`).

## Testing Quirks

- **Unit tests never hit the network**: `tests/unit/conftest.py` monkeypatches `Item.api_json` and `AsyncItem.api_json` to return static JSON from `tests/unit/tests_data/`. When adding new item types, you likely need to add matching JSON fixtures and update the `_api_json` mock dispatcher.
- **Integration tests set up their own data**: `tests/integration/conftest.py` has a session-scoped `setup` fixture that creates folders, jobs, credentials, and views on the live Jenkins instance and tears them down afterward.
- **Integration prerequisites**: Set `JENKINS_URL`, `JENKINS_USER`, and `JENKINS_PASSWORD`. The CI spins `joelee2012/standalone-jenkins:latest` in Docker.
- **pytest-asyncio scope**: `tox.ini` sets `asyncio_default_fixture_loop_scope = session` and passes `--asyncio-mode=auto`.

## Style & Lint

- **Style**: pycodestyle with explicit ignores: `E501,F401,E128,E402,E731,F821`
- **Lint**: ruff
- **Docstrings**: Google style
- **Python support**: 3.8 through 3.13

## CI/CD

- `.github/workflows/unittest.yml` — Runs `tox` (style + lint + unit tests) across Python 3.8–3.13 on ubuntu-latest, uploads coverage for 3.12, and runs `twine check` on the built wheel/sdist.
- `.github/workflows/integration.yml` — Starts Jenkins in Docker, then runs `tox -e integration`.
- `.github/workflows/publish.yml` — Triggered on release creation; builds with `setup.py sdist bdist_wheel` and uploads to PyPI.
