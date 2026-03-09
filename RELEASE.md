Manual release process
======================

The GitHub Action release path is currently not reliable, so releases should be
done manually from a local checkout.

Prerequisites
-------------

1. You have already updated the package version.
2. You have a PyPI API token from [pypi.org](https://pypi.org/manage/account/).

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

Release steps
-------------

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

Tag push reminder
-----------------

If your release tag exists only locally, push it:

```powershell
git push origin main --tags
```
