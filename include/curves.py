"""Helper curves: rough substrate, cantilever and outlined lines."""
import numpy as np


def sawtooth(x, A, w, phase=0):
    L = x[-1] - x[0]
    return A * np.sin(2 * np.pi * w * (x - x[0])/L + phase)


def substrate(x, A, n_modes=10, max_freq=12, rng=None):
    # Sum of modes with random frequencies, amplitudes and phases
    rng = np.random.default_rng(rng)
    freqs = rng.integers(0, max_freq, size=n_modes)
    amplitudes = rng.uniform(0, 1.0, n_modes)
    amplitudes = amplitudes / np.sum(amplitudes) * A
    phases = rng.uniform(0, np.pi, n_modes)
    subs = 0*x
    for f, a, ph in zip(freqs, amplitudes, phases):
        subs += sawtooth(x, a, f, phase=ph)
    return subs


def cantilever(x, alpha=30):
    # Parabola that starts with slope alpha and ends horizontal
    return -np.tan(np.radians(alpha))/2/(x[0]-x[-1])*(x-x[-1])**2


def outlined_plot(ax, x, y, color, lw, outline, outline_color="#000000", **kwargs):
    ax.plot(x, y, color=outline_color, linewidth=lw + outline, **kwargs)
    ax.plot(x, y, color=color, linewidth=lw, **kwargs)
