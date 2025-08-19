# DFB — Delimited File Bundle

AI friendly file format used for bundling multiple text files into one file. Files can later be extracted using a script. DFB (Delimited File Bundle) is a minimal, text-first archive format. Text files remain human-editable; binary files use `ENCODING: base64` so the bundle stays plain text. 

This repository bundle contains:
- `SPEC.md` — the format specification.
- `examples/dfb-example.dfb` — a small example bundle.
- `CONTRIBUTING.md` — contribution notes.
- `LICENSE` — MIT license.
- `logo.svg` — small SVG logo.
- `scripts` — script for extracting dfb data to computer files (or bundling files).

Typical usage
-----------
The format specification can be given to an AI assistant, and the AI assistant can then be asked to output multiple files in the dfb format. This data can then be copied over to the DFB extract script on the computer, and you immediately have all the files on your computer.

Example data
-----------
```language
DFB V1
SEPARATOR: ----DFB-SEP::b3f4e6c0-8a2f-4d1e-9f40-abcdef123456----

----DFB-SEP::b3f4e6c0-8a2f-4d1e-9f40-abcdef123456----
FILENAME: docs/readme.txt
ENCODING: utf-8

Hello — this README is plain UTF-8 text.

----DFB-SEP::b3f4e6c0-8a2f-4d1e-9f40-abcdef123456----
FILENAME: images/icon.png
ENCODING: base64
MIME: image/png

iVBORw0KGgoAAAANSUhEUgAAADAAAAAlAQAAAAAsYlcCAAAACklEQVR4AWMZBQAPOQQNR8+WWwAAAABJRU5ErkJggg==
```

Quick start
-----------
1. Run the python script. A GUI window opens.
2. Paste in the example dfb text and choose a folder on your computer to extract the data to.

License
-------
MIT — see `LICENSE` for the full text.







