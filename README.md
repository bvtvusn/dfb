# DFB — Delimited File Bundle

DFB (Delimited File Bundle) is a minimal, text-first archive format for packaging multiple files into one UTF-8 text file. Text files remain human-editable; binary files use `ENCODING: base64` so the bundle stays plain text.

This repository bundle contains:
- `SPEC.md` — the format specification.
- `examples/dfb-example.dfb` — a small example bundle.
- `CONTRIBUTING.md` — contribution notes.
- `LICENSE` — MIT license.
- `logo.svg` — small SVG logo.

Quick start
-----------
1. Save this bundle as `dfb-bundle.dfb` or paste its contents into a compatible extractor.
2. Extract into a chosen directory (extractors must validate filenames and refuse `..` or absolute paths).

License
-------
MIT — see `LICENSE` for the full text.
