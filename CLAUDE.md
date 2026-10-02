# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`pngify` stores arbitrary data in the pixels of a PNG file and extracts it again. The whole tool is the single module `pngify.py`, which is installed as the `pngify` console script. Packaging metadata lives in `pyproject.toml` (setuptools backend, `requires-python >=3.8`); `setup.py` is only a bare shim for tools such as stdeb that still invoke it. The module uses only the standard library and still carries Python 2 shims (the `from __future__` import and the `stdin`/`stdout` `.buffer` fallbacks), though the package no longer advertises Python 2 support.

## Commands

```sh
python3 pngify.py [-c] [-w WIDTH] input.bin out.png   # encode (-c = zlib-compress payload)
python3 pngify.py out.png restored.bin                # decode (prints original filename to stderr)
python3 pngify.py -p input.bin out.png                # encrypt (prompts for password; needs `pngify[crypto]`)
cat file | python3 pngify.py > out.png                # stdin/stdout are the defaults
pip install -e .                                      # install the `pngify` entry point
python3 -m build                                      # sdist + wheel into dist/ (needs `pip install build`)
```

There is no test suite or linter. To verify a change, do a round trip, with and without `-c` and `-p`, and compare the result with `cmp`.

The `.gitignore` covers `/deb_dist`, which points to Debian packages being built through the `setup.py` shim, probably with stdeb. No build script is checked in.

## Architecture

- **Mode is chosen automatically in `main()`**: if the input starts with the PNG magic bytes it is decoded, otherwise it is encoded. As a result, a PNG file can't be used as the payload.
- **Payload layout** (`PNGWriter.save`), from the outside in:
  1. `>IB` header: payload length, then a flags byte (`COMPRESSED`=1, `ENCRYPTED`=2). Older files wrote a `?` bool here, which reads the same.
  2. if encrypted: `salt(16) | nonce(12) | AES-256-GCM ciphertext+tag`, with the key from `hashlib.scrypt`. Compression happens before encryption. `cryptography` is an optional extra and is imported only when encryption is used.
  3. an optionally zlib-compressed body: a `>H` filename length, the UTF-8 original basename, then the raw data
  4. padding with `0x80` bytes to fill `width*height*3`
- **Image format**: 8-bit RGB (color type 2) with filter type 0 on every scanline, written as a single `IDAT` chunk. The auto width targets roughly a 1.6:1 aspect ratio and is rounded up to a multiple of 160.
- **`PNGReader` is not a general PNG decoder.** It dispatches chunks to `on_<NAME>` handlers and checks CRCs. Each `IDAT` is decompressed separately and must hold the whole image, and any non-zero filter byte raises an error. So it reads only PNGs that `PNGWriter` produced, and changes to the writer's output format must be mirrored in the reader.
