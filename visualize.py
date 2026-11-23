"""Visualizations: linear search vs Grover amplitude amplification.

Produces in images/:
  race.gif          side-by-side animation (linear pointer vs Grover amplitudes)
  scaling.png       queries vs N  (N/2 vs (pi/4)sqrt(N))
  overrotation.png  success probability vs number of Grover iterations

Grover amplitudes are computed with a tiny state-vector simulation in numpy,
so you can see exactly what the oracle and diffuser do.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

os.makedirs("images", exist_ok=True)


def grover_steps(n_items, target, iterations):
    """Yield (label, amplitudes) after each oracle and diffuser step."""
    amps = np.full(n_items, 1 / np.sqrt(n_items))
    yield "Start: equal superposition", amps.copy()
    for i in range(1, iterations + 1):
        amps[target] *= -1                       # oracle: phase flip
        yield f"Iteration {i}: oracle flips target", amps.copy()
        amps = 2 * amps.mean() - amps            # diffuser: reflect about mean
        yield f"Iteration {i}: diffuser amplifies", amps.copy()


def race_gif(n_items=16, target=11):
    iters = int(np.floor(np.pi / 4 * np.sqrt(n_items)))
    g_frames = list(grover_steps(n_items, target, iters))
    n_frames = max(target + 1, len(g_frames)) + 4   # hold the final frame

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    fig.suptitle(f"Searching {n_items} unsorted items for #{target}")

    def draw(f):
        ax1.clear(); ax2.clear()
        checked = min(f, target)
        colors = ["#d62728" if i == target and f > target - 1 else
                  "#1f77b4" if i == checked else
                  "#cccccc" if i < checked else "#eeeeee" for i in range(n_items)]
        ax1.bar(range(n_items), np.ones(n_items), color=colors)
        ax1.set_title(f"Classical linear search: {checked + 1} queries")
        ax1.set_yticks([]); ax1.set_xticks(range(n_items))

        label, amps = g_frames[min(f, len(g_frames) - 1)]
        colors = ["#d62728" if i == target else "#1f77b4" for i in range(n_items)]
        ax2.bar(range(n_items), amps, color=colors)
        ax2.axhline(amps.mean(), ls="--", c="gray", lw=1, label="mean")
        ax2.axhline(0, c="black", lw=0.5)
        ax2.set_ylim(-0.6, 1.05); ax2.set_xticks(range(n_items))
        ax2.set_title(f"Grover: {label}  |  P(target) = {amps[target]**2:.0%}")
        ax2.set_ylabel("amplitude"); ax2.legend(loc="upper left")
        fig.tight_layout()

    anim = FuncAnimation(fig, draw, frames=n_frames, interval=700)
    anim.save("images/race.gif", writer=PillowWriter(fps=1.5))
    plt.close(fig)


def scaling_plot():
    N = np.logspace(1, 6, 200)
    plt.figure(figsize=(7, 4.5))
    plt.loglog(N, N / 2, label="Linear search: N/2 (average)")
    plt.loglog(N, np.pi / 4 * np.sqrt(N), label=r"Grover: $(\pi/4)\sqrt{N}$")
    plt.loglog(N, np.log2(N), "--", c="gray", label=r"Binary search: $\log_2 N$ (needs SORTED data)")
    plt.xlabel("Number of items N"); plt.ylabel("Queries")
    plt.title("Unstructured search: quadratic speedup")
    plt.legend(); plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout(); plt.savefig("images/scaling.png", dpi=150); plt.close()


def overrotation_plot(n_items=64):
    theta = np.arcsin(1 / np.sqrt(n_items))
    k = np.arange(0, 20)
    p = np.sin((2 * k + 1) * theta) ** 2
    best = int(np.floor(np.pi / 4 * np.sqrt(n_items)))
    plt.figure(figsize=(7, 4.5))
    plt.plot(k, p, "o-")
    plt.axvline(best, ls="--", c="red", label=f"optimal = {best} iterations")
    plt.xlabel("Grover iterations"); plt.ylabel("P(find target)")
    plt.title(f"Over-rotation: more iterations is NOT always better (N={n_items})")
    plt.legend(); plt.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("images/overrotation.png", dpi=150); plt.close()


if __name__ == "__main__":
    race_gif()
    scaling_plot()
    overrotation_plot()
    print("Saved images/race.gif, images/scaling.png, images/overrotation.png")
