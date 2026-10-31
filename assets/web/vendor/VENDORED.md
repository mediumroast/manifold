<!-- SPDX-License-Identifier: Apache-2.0 -->
# Vendored web files

The wiki browser's page scripts and styles are served from this folder so the browser needs no
network access. The files are third-party and MIT-licensed; their license texts are in `licenses/`.
Do not edit them by hand: run `python3 tools/vendor_web.py` to rebuild them, or `--check` to compare.

| Package | Version | Tarball integrity (npm registry) |
|---|---|---|
| `docsify` | 4.13.1 | `sha512-BsDypTBhw0mfslw9kZgAspCMZSM+sUIIDg5K/t1hNLkvbem9h64ZQc71e1IpY+iWsi/KdeqfazDfg52y2Lmm0A==` |
| `prismjs` | 1.30.0 | `sha512-DEvV2ZF2r2/63V+tK8hQvrR2ZGn10srHbXviTlcv7Kpzw8jWiNTqbVgjO3IY8RxrrOUF8VPMQQFysYYYv0YZxw==` |
| `docsify-copy-code` | 2.1.1 | `sha512-3+foIMuohrvYTA8dyDwr4wylKSZHXBq4tvoAP24BvzqSM9Rbh0gvXQunVoFZ7If4FOYmUXOBveg3EbJSBUMaow==` |
| `docsify-darklight-theme` | 3.2.0 | `sha512-nAu98+833qcbH/32O7ia3kGk2xnAtCgcQjgjzGgBzmXEmr3jUWcMGcGpf8LJ+C+V4AK00rKng09bUS56H31gcw==` |

Each tarball is checked against the integrity value above before a file is taken from it.
`SHA256SUMS` lists the SHA-256 of every file here; the tests compare it with the files.

## Changes to upstream files

Only `docsify-darklight-theme` is changed, because it reaches out to public hosts at run time (fonts and two icons):

* `darklight.min.css`: the `@import` of Google Fonts is removed. The page falls back to the
  system fonts already named in the style sheet.
* `darklight.min.js`: the two toggle-icon URLs, which pointed at jsDelivr, point at this
  server (`/docs/_manifold/vendor/icons/`), where the icons are served from `icons/`.

Each changed file starts with a comment saying so. All other files are byte-for-byte copies.
