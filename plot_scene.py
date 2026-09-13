"""
Generate analysis plots from a PDW file.

Usage:
    python3 plot_scene.py <pdw_file>

Examples:
    python3 plot_scene.py outputs/validation_fixed/validation_fixed_pdw.txt
    python3 plot_scene.py outputs/mixed_scene/mixed_scene_pdw.txt
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt


def load_pdw(filename):
    """
    Load PDW file.

    Expected columns:
    TOA_us RF_MHz AoA_deg PW_us emitter_id
    """
    return np.loadtxt(filename, skiprows=1)


def plot_rf_vs_toa(data, fig_dir):
    toa = data[:, 0]
    rf = data[:, 1]

    plt.figure(figsize=(8, 4))
    plt.scatter(toa, rf, s=8)

    plt.xlabel("TOA (µs)")
    plt.ylabel("RF (MHz)")
    plt.title("RF vs TOA")

    plt.tight_layout()
    plt.savefig(fig_dir / "rf_vs_toa.png", dpi=300)
    plt.close()


def plot_aoa_vs_toa(data, fig_dir):
    toa = data[:, 0]
    aoa = data[:, 2]

    plt.figure(figsize=(8, 4))
    plt.scatter(toa, aoa, s=8)

    plt.xlabel("TOA (µs)")
    plt.ylabel("AoA (deg)")
    plt.title("AoA vs TOA")

    plt.tight_layout()
    plt.savefig(fig_dir / "aoa_vs_toa.png", dpi=300)
    plt.close()


def plot_pri_validation(data, fig_dir):
    """
    Generate PRI histogram for a validation scene.

    Intended for scenarios containing a single emitter and
    no corruption effects.
    """

    emitter_rows = data[data[:, 4] != 0]

    toa = np.sort(emitter_rows[:, 0])

    if len(toa) < 2:
        return

    pri = np.round(np.diff(toa), 3)

    plt.figure(figsize=(8, 4))

    plt.hist(pri, bins=20)

    plt.xlabel("PRI (µs)")
    plt.ylabel("Count")
    plt.title("PRI Validation")

    plt.tight_layout()
    plt.savefig(fig_dir / "pri_validation.png", dpi=300)
    plt.close()


def plot_emitter_timeline(data, fig_dir):
    toa = data[:, 0]
    emitter = data[:, 4]

    plt.figure(figsize=(8, 4))
    plt.scatter(toa, emitter, s=8)

    plt.xlabel("TOA (µs)")
    plt.ylabel("Emitter ID")
    plt.title("Emitter Timeline")

    plt.tight_layout()
    plt.savefig(fig_dir / "emitter_timeline.png", dpi=300)
    plt.close()


def main(filename):

    data = load_pdw(filename)

    scene_name = Path(filename).stem.replace("_pdw", "")

    fig_dir = Path("figures") / scene_name
    fig_dir.mkdir(parents=True, exist_ok=True)

    plot_rf_vs_toa(data, fig_dir)
    plot_aoa_vs_toa(data, fig_dir)
    plot_pri_validation(data, fig_dir)
    plot_emitter_timeline(data, fig_dir)

    print("\nGenerated figures:")
    print(f"  {fig_dir / 'rf_vs_toa.png'}")
    print(f"  {fig_dir / 'aoa_vs_toa.png'}")
    print(f"  {fig_dir / 'pri_validation.png'}")
    print(f"  {fig_dir / 'emitter_timeline.png'}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("    python3 plot_scene.py <pdw_file>")
        sys.exit(1)

    main(sys.argv[1])
