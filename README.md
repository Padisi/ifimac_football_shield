# IFIMAC shield

Generates the IFIMAC shield as an SVG.

![IFIMAC shield](IFIMAC_shield.svg)

## Usage

```bash
pip install -r requirements.txt
python shield.py                    # -> IFIMAC_shield.svg
python shield.py --seed 42 -o out.svg
python shield.py --params other_parameters.json --palette other_palette.json
```

## Files

| File | Contents |
|---|---|
| `shield.py` | Main script: `draw_shield()` and command-line interface |
| `include/hexagons.py` | Hexagons, half/quarter hexagons and circles on the vertices |
| `include/curves.py` | Random substrate, cantilever and outlined lines |
| `include/c60.py` | C60 fullerene (via ASE) |
| `include/config.py` | Loading of the JSON files |
| `parameters.json` | Geometry, sizes and texts |
| `palette.json` | Colours |

Distances are in data units (the shield lives in `[-extent, extent]²`).
Line widths (`lw`), font sizes (`fs`) and marker sizes (`s`) are in points for a
figure of `ref_figsize` inches and are rescaled with `figsize`. `seed: null` gives a
different substrate on every run.

`parameters.json` and `palette.json` are documented with `//` comments. These are
not standard JSON, so `config.py` strips them before parsing.

## Web version

`index.html` runs `shield.py` in the browser with [Pyodide](https://pyodide.org)
(numpy, matplotlib and ASE compiled to WebAssembly), so it works on GitHub Pages
with no server. It loads the repository's own `shield.py`, `include/` and JSON
files, lets you edit every parameter and colour, and downloads the SVG and the
edited `parameters.json` / `palette.json`. It is published by
`.github/workflows/pages.yml` on every push to `main` (*Settings → Pages → Source:
GitHub Actions*). To try it locally run
`python3 -m http.server 8000` and open http://localhost:8000 (opening the file
directly does not work: browsers block `fetch` from `file://`). `.nojekyll` stops
Jekyll from hiding files that start with `_` if Pages deploys from a branch.
