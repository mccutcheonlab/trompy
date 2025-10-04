Release automation
==================

This repository includes a GitHub Actions workflow `.github/workflows/ci.yml` that:

- runs tests on pushes to `main` and on pull requests
- builds and publishes distributions to PyPI when a tag starting with `v` is pushed (for example `v0.15.8`)

Setup instructions
------------------

1. Create a PyPI API token (on [pypi.org](https://pypi.org/manage/account/)) and store it in the repository secrets as `PYPI_API_TOKEN`.

2. To create a release and upload to PyPI, tag the commit and push the tag:

```powershell
git tag -a v0.15.8 -m "Release v0.15.8"
git push origin v0.15.8
```

The workflow will build the package and publish to PyPI using the token.
