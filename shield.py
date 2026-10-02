"""
Generate the IFIMAC shield as .svg.

Usage:
    python shield.py [--params parameters.json] [--palette palette.json] [-o IFIMAC_shield.svg] [--seed N]

All distances are in data units (the shield lives in [-extent, extent]^2).
Line widths (lw), font sizes (fs) and marker sizes (s) are in points for the
reference figure size figure.ref_figsize and are rescaled automatically with figsize,
so the logo looks identical at any size.
"""
import argparse
import copy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from include.c60 import plot_c60
from include.config import load_palette, load_params
from include.curves import cantilever, outlined_plot, substrate
from include.hexagons import draw_half_hexagon, draw_hexagon, draw_hexagon_circles, draw_quarter_hexagon


def draw_shield(params, palette, figsize=None, ax=None):
    """
    Draw the IFIMAC shield.

    - params: dictionary of parameters (see parameters.json).
    - palette: dictionary of colours (see palette.json).
    - figsize: overrides params["figure"]["figsize"]; a number or a tuple (width, height).
    - ax: existing axis to draw on (if None a new figure is created).

    All point-based sizes are scaled by min(figsize) / ref_figsize,
    so the result is the same drawing at any size.
    """
    P = copy.deepcopy(params)
    F, H, C, T, W, A, M = (P[k] for k in ("figure", "hexagon", "circles", "text", "wave", "afm", "c60"))

    figsize = F["figsize"] if figsize is None else figsize
    if np.isscalar(figsize):
        figsize = (figsize, figsize)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
        figsize = fig.get_size_inches()
    k = min(figsize) / F["ref_figsize"]  # scale factor for everything given in points
    pt = lambda v: v * k

    ax.axis('off')
    ax.set_xlim(-F["extent"], F["extent"])
    ax.set_ylim(-F["extent"], F["extent"])
    ax.set_aspect('equal')  # Keep equal proportions

    # 1. Hexagons
    R = H["R"]
    r = R * H["r_ratio"]
    rim, g = H["rim"], H["gap"]
    lw = pt(H["lw"])

    draw_hexagon(R + rim, 0, 0, ax, facecolor=palette["gold"], edgecolor=palette["black"], linewidth=lw)
    draw_hexagon(R, 0, 0, ax, facecolor=palette["red"], edgecolor=palette["black"], linewidth=lw)

    draw_half_hexagon(r + rim, 0, 0, ax, g - 2*rim, "top", facecolor=palette["gold"], edgecolor=palette["black"], linewidth=lw)
    draw_quarter_hexagon(r, 0, 0, ax, g, quarter="top-left", facecolor=palette["blue"], edgecolor=palette["black"], linewidth=0)
    draw_quarter_hexagon(r, 0, 0, ax, g, quarter="top-right", facecolor=palette["white"], edgecolor=palette["black"], linewidth=0)
    draw_half_hexagon(r, 0, 0, ax, g, "top", facecolor=palette["transparent"], edgecolor=palette["black"], linewidth=lw)

    draw_half_hexagon(r + rim, 0, 0, ax, g - 2*rim, "bottom", facecolor=palette["gold"], edgecolor=palette["black"], linewidth=lw)
    draw_half_hexagon(r, 0, 0, ax, g, "bottom", facecolor=palette["green"], edgecolor=palette["black"], linewidth=lw)

    # 3. Text
    dx, dy = T["shadow_offset"]
    ax.text(dx, dy, T["title"], fontsize=pt(T["title_fs"]), color=palette["black"], ha='center', va='center', fontweight='bold')
    ax.text(0, 0, T["title"], fontsize=pt(T["title_fs"]), color=palette["text"], ha='center', va='center', fontweight='bold')
    delta = T["year_inset"] * R
    x_year = R*np.sqrt(3)/2 - delta
    dx, dy = dx/2, dy/2  # the years' shadow is half the title's
    year_box = dict(facecolor=palette["transparent"], boxstyle='round', edgecolor=palette["transparent"], linewidth=0.0, pad=T["year_pad"])
    ax.text(-x_year+dx, dy, T["years"][0], fontsize=pt(T["year_fs"]), color=palette["black"], ha='left', va='center', fontweight='bold', bbox=year_box)
    ax.text(x_year+dx, dy, T["years"][1], fontsize=pt(T["year_fs"]), color=palette["black"], ha='right', va='center', fontweight='bold', bbox=year_box)
    years = [
        ax.text(-x_year, 0, T["years"][0], fontsize=pt(T["year_fs"]), color=palette["text"], ha='left', va='center', fontweight='bold', bbox=year_box),
        ax.text(x_year, 0, T["years"][1], fontsize=pt(T["year_fs"]), color=palette["text"], ha='right', va='center', fontweight='bold', bbox=year_box),
    ]

    # 2. Circles on the vertices, with a gap as tall as the year boxes
    fig.canvas.draw()  # needed to know the actual size of the boxes
    inv = ax.transData.inverted()
    year_gap = max(np.ptp(inv.transform(t.get_bbox_patch().get_window_extent().get_points())[:, 1]) for t in years)
    draw_hexagon_circles((r + R + rim)/2, 0, 0, ax, C["r"], ratio=C["ratio"],
                         line_lw=pt(C["lw"]), outline=pt(C["outline"]), gap=year_gap + 2 * C["gap_margin"],
                         line_color=palette["white"],
                         facecolor=palette["white"], edgecolor=palette["black"], linewidth=pt(C["lw"]))

    # 4. Wave packet between two two-level systems
    x = np.linspace(-W["half_length"], W["half_length"], W["n"])
    y = W["A"]*np.sin(W["w"]*(x-x[0]/2))*np.exp(-W["gamma"]*(x-x[0]/2-x[-1]/2)**2)
    a = np.radians(W["angle"])
    x_rot = x*np.cos(a) - y*np.sin(a) + W["center"][0]
    y_rot = x*np.sin(a) + y*np.cos(a) + W["center"][1]
    outlined_plot(ax, x_rot, y_rot, palette["white"], pt(W["lw"]), pt(W["outline"]), palette["black"])
    hw, dl = W["level_half_width"], W["level_dy"]
    for xe, ye in [(x_rot[0], y_rot[0]), (x_rot[-1], y_rot[-1])]:
        ax.scatter(xe, ye, color=palette["white"], s=W["qubit_s"]*k**2, linewidth=pt(W["qubit_lw"]), edgecolor=palette["black"], zorder=5)
        # Two lines inside the marker: two-level system
        for s in (1, -1):
            ax.plot([xe-hw, xe+hw], [ye+s*dl, ye+s*dl], color=palette["black"], linewidth=pt(W["qubit_lw"]), zorder=6)

    # 5. AFM tip over a rough substrate
    x = np.linspace(-A["sub_half_length"], A["sub_half_length"], A["sub_n"])
    y_sub = substrate(x, A["sub_A"], A["sub_n_modes"], A["sub_max_freq"], rng=F["seed"]) + A["sub_y"]
    outlined_plot(ax, x + A["center_x"], y_sub, palette["blue"], pt(A["sub_lw"]), pt(A["sub_outline"]), palette["black"])

    x_cant = np.linspace(*A["cant_x"], 100)
    y_cant = cantilever(x_cant, alpha=A["cant_alpha"]) + A["cant_y"]
    x_cant = x_cant + A["center_x"]
    outlined_plot(ax, x_cant, y_cant, palette["blue"], pt(A["cant_lw"]), pt(A["cant_outline"]), palette["black"])

    tw, th = A["tip_width"], A["tip_height"]
    xt, yt = x_cant[-1], y_cant[-1]
    vertex = np.array([[xt - tw/2, yt - th], [xt - tw, yt], [xt, yt]])
    ax.add_patch(Polygon(vertex, closed=True, facecolor=palette["blue"], edgecolor=palette["black"], linewidth=pt(A["tip_lw"])))

    # 6. C60 fullerene
    plot_c60(*M["center"], ax, radius=M["radius"], theta=M["theta"], phi=M["phi"], cutoff=M["cutoff"],
             lw=pt(M["lw"]), outline=pt(M["outline"]), color=palette["white"], outline_color=palette["black"])

    return fig, ax


def main():
    parser = argparse.ArgumentParser(description="Generate the IFIMAC shield as .svg")
    parser.add_argument("--params", default=None, help="path to parameters.json")
    parser.add_argument("--palette", default=None, help="path to palette.json")
    parser.add_argument("-o", "--output", default=None, help="output file (default: figure.filename)")
    parser.add_argument("--seed", type=int, default=None, help="substrate seed (overrides figure.seed)")
    args = parser.parse_args()

    params = load_params(args.params) if args.params else load_params()
    palette = load_palette(args.palette) if args.palette else load_palette()
    if args.seed is not None:
        params["figure"]["seed"] = args.seed
    filename = args.output or params["figure"]["filename"]

    fig, _ = draw_shield(params, palette)
    fig.savefig(filename, format=filename.rsplit(".", 1)[-1])
    print(f"Shield saved to {filename}")


if __name__ == "__main__":
    main()
