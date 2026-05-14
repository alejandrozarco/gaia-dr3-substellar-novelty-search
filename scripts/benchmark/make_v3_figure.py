"""v3 benchmark figure — v2 vs v3 cascade comparison."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import get_args  # noqa: E402

args = get_args(description="Generate v3 cascade comparison figure")
OUT_DIR = str(args.out_dir)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 7),
                                gridspec_kw={"width_ratios": [1, 1.3]})

# Panel L — metric comparison
metrics = ["In-pool\nnovelty recall", "End-to-end\nnovelty recall",
           "End-to-end\nspecificity", "Documented-FP\ncatch (Filter #27)"]
v2_vals = [58.8, 42.6, 72.7, 100.0]
v3_vals = [85.3, 61.7, 72.7, 100.0]

x = np.arange(len(metrics))
width = 0.35

bars_v2 = axL.bar(x - width / 2, v2_vals, width, color="#aaaaaa",
                   edgecolor="black", linewidth=0.7, label="v2 (released)")
bars_v3 = axL.bar(x + width / 2, v3_vals, width, color="#2ca02c",
                   edgecolor="black", linewidth=0.7,
                   label="v3 (Sahlmann tie-breaking)")

# Value labels
for bars, vals in [(bars_v2, v2_vals), (bars_v3, v3_vals)]:
    for bar, v in zip(bars, vals):
        axL.text(bar.get_x() + bar.get_width() / 2, v + 1.5,
                 f"{v:.1f}%", ha="center", fontsize=10, fontweight="bold")

# Delta arrows for the changed metrics
for i in [0, 1]:
    delta = v3_vals[i] - v2_vals[i]
    if delta > 0:
        axL.annotate(f"+{delta:.1f}pp", xy=(x[i], (v2_vals[i] + v3_vals[i]) / 2),
                     ha="center", fontsize=10, color="darkgreen", fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#e8f5e8",
                               edgecolor="green", linewidth=0.7))

axL.set_xticks(x)
axL.set_xticklabels(metrics, fontsize=10)
axL.set_ylabel("Percent", fontsize=11)
axL.set_ylim(0, 115)
axL.set_yticks([0, 25, 50, 75, 100])
axL.set_title("v2 vs v3 cascade — headline metrics", fontsize=12, fontweight="bold")
axL.grid(axis="y", alpha=0.3)
axL.legend(loc="lower right", fontsize=10, framealpha=0.95)
axL.axhline(100, color="gray", lw=0.5, ls=":")

# Panel R — what changed for the 12 reclassified sources
sources = [
    "BD+29 1539",   "HD 82460",     "HD 68638A",
    "HD 52756",     "HD 91669",     "HD 92320",
    "BD-00 4475",   "HD 89707",     "CD-46 10046",
    "HD 77065",     "HD 5433",      "HD 30246",
]
v3_verdicts = [
    "CORROBORATED",  "CORROBORATED",  "FLAG",
    "CORROBORATED",  "REJECTED_RUWE", "SURVIVOR",
    "REJECTED_RUWE", "FLAG",          "SURVIVOR",
    "CORROBORATED",  "REJECTED_RUWE", "FLAG",
]
verdict_colors = {
    "CORROBORATED": "#1f7a3a",
    "FLAG":         "#2ca02c",
    "SURVIVOR":     "#90c890",
    "REJECTED_RUWE": "#d62728",
}

y_pos = np.arange(len(sources))
for i, (src, v) in enumerate(zip(sources, v3_verdicts)):
    color = verdict_colors[v]
    axR.barh(i, 1.0, color=color, edgecolor="black", linewidth=0.5)
    axR.text(0.5, i, f"{src}    →    {v}", ha="center", va="center",
             fontsize=9, color="white" if v in ["CORROBORATED", "REJECTED_RUWE"]
             else "black", fontweight="bold")

axR.set_yticks([])
axR.set_xticks([])
axR.set_xlim(0, 1)
axR.invert_yaxis()
axR.set_title(
    "12 CONFIRMED_BROWN_DWARFs previously rejected as Sahlmann ML imposter\n"
    "→ reclassified under v3 tie-breaking rule",
    fontsize=11.5, fontweight="bold")

# Legend for panel R
legend_handles = [plt.Rectangle((0, 0), 1, 1, color=c, edgecolor="black",
                                 linewidth=0.5)
                  for c in [verdict_colors["CORROBORATED"],
                            verdict_colors["FLAG"],
                            verdict_colors["SURVIVOR"],
                            verdict_colors["REJECTED_RUWE"]]]
legend_labels = [
    "CORROBORATED (4 — strong retained)",
    "FLAG (3 — weak retained)",
    "SURVIVOR (2 — weak retained)",
    "REJECTED_RUWE (3 — still rejected, different reason)",
]
axR.legend(legend_handles, legend_labels, loc="upper center",
           bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=9)

fig.suptitle(
    "v3 cascade Sahlmann tie-breaking — benchmark improvement\n"
    "Recall: 58.8% → 85.3% (+26.5pp), specificity unchanged",
    fontsize=13.5, fontweight="bold", y=1.00)

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/benchmark_v3_figure.png", dpi=300, bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"Wrote {OUT_DIR}/benchmark_v3_figure.png")
