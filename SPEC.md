# DFB V1 — Specification

**Purpose**  
DFB V1 is a small, text-first archive format for bundling multiple files into one text file. It is easy to implement and review.

**Top-level layout**
1. Header (first line): `DFB V1`
2. Control block (ASCII `KEY: value` lines), terminated by one blank line. **Required** key:
   - `SEPARATOR: <separator-line>` — a long, newline-free ASCII string (preferrably including a UUID); generate a fresh separator per-archive.
3. Entries (zero or more). Each entry:
   - A line exactly equal to the separator.
   - A metadata block (`KEY: value` lines), terminated by a blank line.
   - A file content block (text or encoded text) until the next separator or EOF.

**Per-entry metadata**
- Required: `FILENAME: <utf-8 relative path>` (use POSIX forward slashes)
- Recommended: `ENCODING: utf-8 | base64` (default `utf-8`)
- Optional: `MIME: <type>`, `MTIME: <ISO-8601>`

**Parsing summary**
- Read as UTF-8 text. Verify header equals `DFB V1`.
- Read control block and extract `SEPARATOR:` (required).
- Find separator lines that match exactly (line equals separator).
- For each entry: parse metadata until blank line, then capture content until next separator or EOF.
- If `ENCODING: base64`, join content lines, strip whitespace, base64-decode to bytes and write binary. If `utf-8`, write content as UTF-8 text exactly as present.

**Security**
- Validate `FILENAME`: reject absolute paths and any `..` segments. Resolve paths under extraction root and ensure they cannot escape it.
- Document and enforce a duplicate-file policy (fail/overwrite/rename).

**Notes**
- No per-file lengths are stored. To minimize collision risk, use long per-archive separators (UUIDs). For absolute binary robustness consider a future length-prefixed variant.

**Example data**
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
