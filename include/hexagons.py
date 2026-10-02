"""Regular hexagons (full, halves and quarters) and circles on their vertices."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon


def hexagon_vertices(r, x, y, closed=True):
    angles = np.linspace(np.pi/2, 2 * np.pi + np.pi/2, 7)  # 6 sides + closing point
    if not closed:
        angles = angles[:-1]
    return np.column_stack([x + r * np.cos(angles), y + r * np.sin(angles)])


def draw_hexagon(r, x, y, ax, **kwargs):
    """
    Draw a regular hexagon on a Matplotlib axis.

    Parameters:
    - r: Radius of the hexagon.
    - x, y: Coordinates of the centre of the hexagon.
    - ax: Matplotlib axis to draw on.
    - kwargs: Extra arguments for Polygon.
    """
    ax.add_patch(Polygon(hexagon_vertices(r, x, y), closed=True, **kwargs))


def draw_half_hexagon(r, x, y, ax, gap, side="top", **kwargs):
    """
    Draw the top or bottom half of a regular hexagon, clipped by the
    horizontal line y = y ± gap/2 (leaves a band of height gap between halves).

    Parameters:
    - r: Radius of the hexagon.
    - x, y: Centre of the full hexagon.
    - ax: Matplotlib axis.
    - gap: Total height of the band between the top and bottom halves.
    - side: "top" or "bottom".
    - kwargs: Extra arguments for Polygon.
    """
    verts = hexagon_vertices(r, x, y, closed=False)

    s = 1 if side == "top" else -1
    cut = y + s * gap / 2
    inside = lambda p: s * (p[1] - cut) >= 0

    # Sutherland–Hodgman clipping against the half-plane s*(y - cut) >= 0
    points = []
    for i in range(len(verts)):
        p, q = verts[i], verts[(i + 1) % len(verts)]
        if inside(p):
            points.append(p)
        if inside(p) != inside(q):
            t = (cut - p[1]) / (q[1] - p[1])
            points.append(p + t * (q - p))

    ax.add_patch(Polygon(np.array(points), closed=True, **kwargs))


def draw_quarter_hexagon(r, x, y, ax, gap, quarter="top-left", **kwargs):
    """
    Draw a quarter of a regular hexagon, clipped by the horizontal line
    y = y ± gap/2 and by the vertical line through the centre.

    Parameters:
    - r: Radius of the hexagon.
    - x, y: Centre of the full hexagon.
    - ax: Matplotlib axis.
    - gap: Total height of the band between the top and bottom halves.
    - quarter: "top-left", "top-right", "bottom-left" or "bottom-right".
    - kwargs: Extra arguments for Polygon.
    """
    verts = hexagon_vertices(r, x, y, closed=False)
    cutx = x

    if quarter == "top-left":
        cuty = y + gap / 2
        verts = np.append(verts, [[x, cuty]], axis=0)  # Add the corner of the quarter
        inside = lambda p: (p[1] >= cuty) and (p[0] <= cutx)
    elif quarter == "top-right":
        cuty = y + gap / 2
        verts = np.append(verts, [[x, cuty]], axis=0)
        verts[2:] = verts[1:-1]  # Insert the corner right after the top vertex
        verts[1] = [x, cuty]
        inside = lambda p: (p[1] >= cuty) and (p[0] >= cutx)
    elif quarter == "bottom-left":
        cuty = y - gap / 2
        verts = np.append(verts, [[x, cuty]], axis=0)
        inside = lambda p: (p[1] <= cuty) and (p[0] <= cutx)
    elif quarter == "bottom-right":
        cuty = y - gap / 2
        verts = np.append(verts, [[x, cuty]], axis=0)
        inside = lambda p: (p[1] <= cuty) and (p[0] >= cutx)
    else:
        raise ValueError("quarter must be one of 'top-left', 'top-right', 'bottom-left', 'bottom-right'")

    # Sutherland–Hodgman clipping against the horizontal and vertical lines
    points = []
    for i in range(len(verts)):
        p, q = verts[i], verts[(i + 1) % len(verts)]
        if inside(p):
            points.append(p)
        if inside(p) != inside(q):
            if (p[1] - cuty) * (q[1] - cuty) < 0:  # Horizontal intersection
                t = (cuty - p[1]) / (q[1] - p[1])
                points.append(p + t * (q - p))
            elif (p[0] - cutx) * (q[0] - cutx) < 0:  # Vertical intersection
                t = (cutx - p[0]) / (q[0] - p[0])
                points.append(p + t * (q - p))

    ax.add_patch(Polygon(np.array(points), closed=True, **kwargs))


def draw_hexagon_circles(r, x, y, ax, cr, ratio=0.5, line_lw=1.0, outline=1.0, gap=0.0,
                         line_color="white", **kwargs):
    """
    Draw circles on every vertex of a regular hexagon, joined by lines
    that do not touch the circles.

    Parameters:
    - r: Radius of the hexagon.
    - x, y: Centre of the hexagon.
    - ax: Matplotlib axis.
    - cr: Radius of the circles.
    - ratio: Fraction of each side (from each end) left uncovered by the line.
    - line_lw: Width of the line between circles.
    - outline: Extra width of the black outline of those lines.
    - gap: Gap (data units) in the middle of the vertical sides, where the years go.
    - line_color: Colour of the line between circles.
    - kwargs: Extra arguments for plt.Circle.
    """
    points = hexagon_vertices(r, x, y)
    edgecolor = kwargs.get('edgecolor', 'black')

    # Lines have "projecting" caps: they stick out half their width beyond the end point.
    # Compensate for it so that the visible gap is exactly gap.
    cap_px = (line_lw + 2 * outline) / 2 * ax.figure.dpi / 72
    cap = np.diff(ax.transData.inverted().transform([(0, 0), (0, cap_px)])[:, 1])[0]

    for p1, p2 in zip(points[:-1], points[1:]):
        start = p1 + (p2 - p1) * ratio
        end = p2 - (p2 - p1) * ratio
        segments = [(start, end)]
        if gap > 0 and np.isclose(p1[0], p2[0]):  # vertical side: split the line in two
            mid = (start + end) / 2
            u = (end - start) / np.linalg.norm(end - start)
            half = gap / 2 + cap
            segments = [(start, mid - u * half), (mid + u * half, end)]
        for a, b in segments:
            ax.plot([a[0], b[0]], [a[1], b[1]], color=edgecolor, linewidth=line_lw + 2 * outline)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=line_color, linewidth=line_lw)

    for (vx, vy) in points[:-1]:  # Skip the last point, which equals the first one
        ax.add_patch(plt.Circle((vx, vy), cr, **kwargs))
