Release process
===============

GitHub Actions is the primary release path.
Pushing a version tag (`v*`) triggers CI tests and then publishes to PyPI.
Manual `twine` upload is documented below as a fallback.

Prerequisites
-------------

1. You have write access to this repository.
2. Repository secret `PYPI_API_TOKEN` is configured in GitHub.
3. You have write access to the target project on PyPI.

Prepare version and changelog
-----------------------------

1. Update `trompy/_version.py` to the new release version.

Example:

```python
__version__ = "0.15.9"
```

2. Update `changelog.txt` with a new top entry for the same version and date.

Example:

```text
0.15.9 - 2026-03-09
- Short bullet describing the main change
- Short bullet describing another change
```

3. Commit both files before creating the release tag.

```powershell
git add trompy/_version.py changelog.txt
git commit -m "Bump version to 0.15.9 and update changelog"
```

Create and push release tag
---------------------------

Create an annotated tag that matches the version, then push commit and tag.

```powershell
git tag -a v0.15.9 -m "Release v0.15.9"
git push origin main
git push origin v0.15.9
```

Automatic publish via GitHub Actions
------------------------------------

After pushing `v0.15.9`, GitHub Actions workflow `CI` will:

1. Run tests.
2. Build source and wheel distributions.
3. Publish to PyPI from the tag commit.

Verify in GitHub Actions that `Build & Publish` is successful.

Manual fallback (if Actions fails)
----------------------------------

Run all commands from the repository root.

```powershell
# Optional: remove old build artifacts first
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# Ensure release tools are up to date
python -m pip install --upgrade build twine

# Build source distribution and wheel
python -m build

# Validate package metadata and distributions
python -m twine check dist/*

# Upload to PyPI using API token authentication
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-xxxxxxxxxxxxxxxx"
python -m twine upload dist/*
```

Optional test upload
--------------------

Use TestPyPI first if you want a dry run:

```powershell
python -m twine upload --repository testpypi dist/*
```

Troubleshooting
---------------

1. Error: Python `3.1` not found on Ubuntu.
	Cause: YAML parsed `3.10` as `3.1`.
	Fix: Quote all workflow matrix versions (for example `'3.10'`).

2. Error: `Invalid or non-existent authentication information` during publish.
	Cause: Missing or incorrect GitHub secret.
	Fix: Set repo secret `PYPI_API_TOKEN` to a valid PyPI API token.

3. Error: `File already exists` from PyPI.
	Cause: Attempting to upload a version that is already published.
	Fix: Bump `trompy/_version.py`, update `changelog.txt`, create a new tag, and push again.

4. Release job does not run after tag push.
	Cause: Tag does not match trigger pattern.
	Fix: Use tags in the format `vX.Y.Z` and push the tag (`git push origin vX.Y.Z`).

5. Tests pass locally but fail in CI.
	Cause: Environment mismatch or missing dependency pins.
	Fix: Recreate a clean environment, verify `requirements.txt`, and run `pytest -q` before tagging.

Tag push reminder
-----------------

If your release tag exists only locally, push it:

```powershell
git push origin main --tags
```
