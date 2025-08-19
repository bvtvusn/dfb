# DFB — Delimited File Bundle

DFB (Delimited File Bundle) is a minimal, AI friendly, text-first archive format for packaging multiple files into one UTF-8 text file. Text files remain human-editable; binary files use `ENCODING: base64` so the bundle stays plain text. 

This repository bundle contains:
- `SPEC.md` — the format specification.
- `examples/dfb-example.dfb` — a small example bundle.
- `CONTRIBUTING.md` — contribution notes.
- `LICENSE` — MIT license.
- `logo.svg` — small SVG logo.

Typical usage
-----------
The format specification can be given to an AI assistant, and the AI assistant can then be asked to output multiple files in the dfb format. This data can then be copied over to the DFB extract script on the computer, and you immediately have all the files on your computer.

Quick start
-----------
1. Save this bundle as `dfb-bundle.dfb` or paste its contents into a compatible extractor.
2. Extract into a chosen directory (extractors must validate filenames and refuse `..` or absolute paths).

License
-------
MIT — see `LICENSE` for the full text.


