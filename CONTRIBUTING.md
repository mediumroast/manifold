# Contributing

Contributions are welcome. The details for the base bundle are in [`bundles/base/CONTRIBUTING.md`](bundles/base/CONTRIBUTING.md); in short:

- Contributions are licensed under the Apache License 2.0.
- Sign off every commit (`git commit -s`) to certify the [Developer Certificate of Origin](https://developercertificate.org/).
- Keep it generic: no company, product or customer names, and no project-specific paths.

Before opening a pull request, run these from the repository root; both must pass:

```bash
python bundles/base/tools/build.py --check
python -m pytest bundles/base/tests -q
```

Open pull requests against `main`. Pull requests are squash-merged.
