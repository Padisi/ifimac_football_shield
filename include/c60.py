"""Drawing of the C60 fullerene."""
import numpy as np
from ase.build import molecule
from ase.neighborlist import NeighborList


def plot_c60(x0, y0, ax, radius=1.0, theta=300, phi=0, cutoff=0.77, lw=1.0, outline=0.5,
             color="#FFFFFF", outline_color="#000000"):
    # Load fullerene C60 and rotate it to have a better view
    atoms = molecule("C60")
    atoms.rotate("x", theta, rotate_cell=True)
    atoms.rotate("z", phi, rotate_cell=True)
    pos = atoms.get_positions() * radius + np.array([x0, y0, 0])

    # Create bond list from covalent radii
    nl = NeighborList([cutoff] * len(atoms), self_interaction=False, bothways=True)
    nl.update(atoms)

    # Draw bonds: black outline below and white line on top; back bonds stay behind
    for i in range(len(atoms)):
        neighbors, _ = nl.get_neighbors(i)
        for j in neighbors:
            if j > i:  # avoid drawing twice
                p1, p2 = pos[i], pos[j]
                depth = np.sign(p1[2] + p2[2])
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=outline_color,
                        lw=lw + outline, zorder=9 + depth)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color,
                        lw=lw, zorder=10 + depth)
