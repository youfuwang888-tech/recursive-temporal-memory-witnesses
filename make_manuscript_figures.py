"""Generate vector figures for the temporal-memory manuscript."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "manuscript" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def save(fig, name: str):
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def protocol_figure():
    fig, ax = plt.subplots(figsize=(7.2, 2.25))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")

    memory = FancyBboxPatch(
        (0.35, 0.75),
        1.65,
        1.5,
        boxstyle="round,pad=0.04",
        facecolor="#e8f1f8",
        edgecolor="#1f4e79",
        linewidth=1.2,
    )
    ax.add_patch(memory)
    ax.text(1.175, 1.78, "internal", ha="center", va="center", weight="bold")
    ax.text(1.175, 1.56, "memory", ha="center", va="center", weight="bold")
    ax.text(1.175, 1.18, "dimension $d$", ha="center", va="center")

    x_positions = [2.8, 4.45, 6.1, 7.75]
    for idx, x in enumerate(x_positions, start=1):
        box = FancyBboxPatch(
            (x, 1.05),
            1.05,
            0.9,
            boxstyle="round,pad=0.03",
            facecolor="#f7f7f7",
            edgecolor="#333333",
        )
        ax.add_patch(box)
        ax.text(
            x + 0.525,
            1.5,
            r"$\mathcal{I}$",
            ha="center",
            va="center",
            fontsize=13,
        )
        ax.text(x + 0.525, 0.72, f"$a_{idx}\\in\\{{0,1\\}}$", ha="center")
        if idx == 1:
            start_x = 2.0
        else:
            start_x = x_positions[idx - 2] + 1.05
        ax.add_patch(
            FancyArrowPatch(
                (start_x, 1.5),
                (x, 1.5),
                arrowstyle="-|>",
                mutation_scale=10,
                linewidth=1.0,
                color="#333333",
            )
        )
    ax.add_patch(
        FancyArrowPatch(
            (8.8, 1.5),
            (9.65, 1.5),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.0,
            color="#333333",
        )
    )
    ax.text(9.15, 1.92, "$\\cdots$", ha="center", fontsize=13)
    ax.text(
        5.55,
        2.55,
        "same stationary binary instrument at every step",
        ha="center",
        weight="bold",
    )
    ax.text(
        5.55,
        0.2,
        "external stopping length; no clock, index, or round label enters the device",
        ha="center",
        color="#8b1a1a",
    )
    save(fig, "fig1_protocol")


def complexity_figure():
    levels = np.arange(2, 13)
    lengths = 2**levels
    dc = 3 * lengths / 4
    fig, ax = plt.subplots(figsize=(4.6, 3.25))
    ax.plot(lengths, dc, "o-", color="#1f77b4", label=r"$DC(T_n)=3N/4$")
    ax.plot(lengths, lengths, "--", color="#777777", label="$N$")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("word length $N=2^n$")
    ax.set_ylabel("deterministic memory states")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False)
    ax.set_title("Autonomous finite-word generation")
    save(fig, "fig2_dc_scaling")


def separation_figure():
    labels = [r"$T_3$ ($L=8$)", r"$T_4$ ($L=16$)"]
    classical_candidate = np.array(
        [0.016434148019480888, 9.488079226956014e-05]
    )
    classical_upper = np.array([0.03, 0.0005])
    quantum = np.array([0.041469816596040404, 0.0006964519920865576])
    x = np.arange(2)
    width = 0.24
    fig, ax = plt.subplots(figsize=(4.8, 3.25))
    ax.bar(
        x - width,
        classical_candidate,
        width=width,
        color="#7f7f7f",
        label="classical construction",
    )
    ax.bar(
        x,
        classical_upper,
        width=width,
        color="#b22222",
        label="certified classical upper",
    )
    ax.bar(
        x + width,
        quantum,
        width=width,
        color="#2b6cb0",
        label="certified qubit lower",
    )
    ax.set_xticks(x, labels)
    ax.set_ylabel("target-word probability")
    ax.set_yscale("log")
    ax.set_ylim(5e-5, 7e-2)
    ax.grid(True, which="both", axis="y", alpha=0.22)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("Two-scale dimension-two separation")
    save(fig, "fig3_certified_separation")


def robustness_figure():
    data = json.loads(
        (ROOT / "outputs/thue_morse_L8_d2_noise_and_shots.json").read_text(
            encoding="utf-8"
        )
    )
    table = data["noise_table"]
    eta = np.array([row["eta"] for row in table])
    probability = np.array([row["target_word_probability"] for row in table])
    order = np.argsort(eta)
    fig, ax = plt.subplots(figsize=(4.8, 3.25))
    ax.plot(100 * eta[order], probability[order], "o-", color="#2b6cb0")
    ax.axhline(0.03, color="#b22222", linewidth=1.6, label="classical bound")
    critical = 100 * data["critical_eta_where_probability_equals_0p03"]
    ax.axvline(critical, color="#333333", linestyle="--", linewidth=1.0)
    ax.text(critical + 0.25, 0.031, f"$\\eta_c={critical:.2f}\\%$", fontsize=8)
    ax.set_xlabel("registered per-round noise $\\eta$ (%)")
    ax.set_ylabel(r"$P(01101001)$")
    ax.set_title("Conditional noise robustness")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "fig4_noise_robustness")


if __name__ == "__main__":
    protocol_figure()
    complexity_figure()
    separation_figure()
    robustness_figure()
    print(f"Figures written to {FIGURES}")
