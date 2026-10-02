"""Loading of parameters.json and palette.json (JSON with // comments)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def strip_comments(text):
    """Remove // comments outside strings, so JSON files can be documented inline."""
    out, in_string, escaped, i = [], False, False, 0
    while i < len(text):
        c = text[i]
        if in_string:
            out.append(c)
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
            out.append(c)
        elif text.startswith("//", i):
            while i < len(text) and text[i] != "\n":  # skip until end of line
                i += 1
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(strip_comments(f.read()))


def load_params(path=ROOT / "parameters.json"):
    return load_json(path)


def load_palette(path=ROOT / "palette.json"):
    return load_json(path)
