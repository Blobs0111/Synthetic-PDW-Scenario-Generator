"""Generate every figure used in LAB.md.

Run from anywhere:

    python3 figs/make_figs.py

Writes PNGs into the same folder as this script (figs/). The figures are pure
demonstrations of the equations in LAB.md — they intentionally reimplement the
TOA generators in a few lines each so the math->code mapping is visible in one
place. Your own emitters.py implementations should match these.

All plots: Agg backend, white background, dpi=130, titled/labelled/legended.
"""
import os

import matplotlib

matplotlib.use("Agg")  # headless: render straight to PNG, no display needed
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------------
# House style
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
DPI = 130
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 10,
})


def save(fig, name):
    """Save a figure into figs/ and report the path."""
    path = os.path.join(HERE, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}")
    return path


# ----------------------------------------------------------------------------
# Reference TOA generators (mirror emitters.py; kept tiny on purpose)
# ----------------------------------------------------------------------------
def toas_fixed(pri, t_end, rng):
    """Fixed PRI:  t_n = t0 + n*T,  t0 ~ U(0, T)."""
    t0 = rng.uniform(0, pri)
    return np.arange(t0, t_end, pri)


def toas_stagger(pattern, t_end, rng):
    """Staggered PRI: cycle through a fixed pattern of M intervals."""
    pattern = list(pattern)
    t = rng.uniform(0, pattern[0])
    out, k = [t], 0
    while t < t_end:
        t = t + pattern[k % len(pattern)]
        out.append(t)
        k += 1
    out = np.asarray(out)
    return out[out < t_end]


def toas_jitter(mean, jitter, t_end, rng):
    """Jittered PRI: T_n ~ N(mean, jitter^2), TOAs = cumulative sum."""
    # over-generate intervals, cumulative-sum, then clip to the window
    n_guess = int(t_end / mean * 1.5) + 10
    intervals = rng.normal(mean, jitter, n_guess)
    intervals = np.clip(intervals, 1e-6, None)  # PRI can't be <= 0
    t0 = rng.uniform(0, mean)
    t = t0 + np.cumsum(intervals)
    return t[t < t_end]


def toas_dwell(pris, dwell, t_end, rng):
    """Dwell-switched: hold PRI A for `dwell` us, then switch to B, cycling."""
    pris = list(pris)
    t = rng.uniform(0, pris[0])
    out, block_start, b = [], t, 0
    while t < t_end:
        out.append(t)
        pri = pris[b % len(pris)]
        t = t + pri
        if t - block_start >= dwell:      # dwell block finished -> switch PRI
            block_start = t
            b += 1
    out = np.asarray(out)
    return out[out < t_end]


# ----------------------------------------------------------------------------
# FIG 1 — TOA stems for fixed / staggered / jittered PRI
# ----------------------------------------------------------------------------
def fig_toa_types():
    rng = np.random.default_rng(1)
    win = 6000.0  # 6 ms window, in microseconds

    tf = toas_fixed(500, win, rng)
    ts = toas_stagger([400, 500, 650], win, rng)
    tj = toas_jitter(500, 90, win, rng)

    fig, axes = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
    data = [
        (tf, "Fixed PRI  (T = 500 us): even spacing", "tab:blue"),
        (ts, "Staggered PRI  (pattern [400, 500, 650] us): repeating spacing", "tab:green"),
        (tj, "Jittered PRI  (mean 500 us, sigma 90 us): wobbly spacing", "tab:red"),
    ]
    for ax, (t, title, color) in zip(axes, data):
        ax.stem(t, np.ones_like(t), linefmt=color, markerfmt=" ", basefmt=" ")
        ax.set_title(title, fontsize=10)
        ax.set_yticks([])
        ax.set_ylim(0, 1.2)
    axes[-1].set_xlabel("Time of arrival, TOA (us)")
    fig.suptitle("Pulse trains as TOA sequences {t_n}", fontsize=12, y=1.0)
    fig.tight_layout()
    save(fig, "fig_toa_types.png")


# ----------------------------------------------------------------------------
# FIG 2 — PRI (inter-pulse-interval) histograms
# ----------------------------------------------------------------------------
def fig_pri_hist():
    rng = np.random.default_rng(2)
    win = 200_000.0  # 200 ms => lots of intervals for a smooth histogram

    df = np.diff(toas_fixed(500, win, rng))
    ds = np.diff(np.sort(toas_stagger([400, 500, 650], win, rng)))
    dj = np.diff(toas_jitter(500, 60, win, rng))

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))

    axes[0].hist(df, bins=np.linspace(480, 520, 60), color="tab:blue")
    axes[0].set_title("Fixed: single delta spike")

    axes[1].hist(ds, bins=np.linspace(350, 700, 80), color="tab:green")
    axes[1].set_title("Staggered: discrete peaks (400/500/650)")

    axes[2].hist(dj, bins=40, color="tab:red")
    axes[2].set_title("Jittered: Gaussian bell")

    for ax in axes:
        ax.set_xlabel("PRI = t_{n} - t_{n-1}  (us)")
        ax.set_ylabel("count")
    fig.suptitle("Inter-pulse-interval histograms distinguish PRI type", fontsize=12)
    fig.tight_layout()
    save(fig, "fig_pri_hist.png")


# ----------------------------------------------------------------------------
# FIG 3 — interleaved scene: RF vs TOA for 3 emitters
# ----------------------------------------------------------------------------
def fig_interleaved():
    rng = np.random.default_rng(3)
    win = 40_000.0  # 40 ms

    emitters = [
        ("Emitter A  9.2 GHz fixed", toas_fixed(516, win, rng), 9.2, "tab:blue", "o"),
        ("Emitter B  2.9 GHz fixed", toas_fixed(1300, win, rng), 2.9, "tab:orange", "s"),
        ("Emitter C  6.5 GHz stagger", toas_stagger([466, 566], win, rng), 6.5, "tab:green", "^"),
    ]

    fig, ax = plt.subplots(figsize=(9, 4.2))
    for label, t, rf_ghz, color, marker in emitters:
        rf = rf_ghz + rng.normal(0, 0.003, len(t))  # small RF measurement scatter
        ax.scatter(t / 1000.0, rf, s=18, c=color, marker=marker, label=label, alpha=0.8)
    ax.set_xlabel("TOA (ms)")
    ax.set_ylabel("RF (GHz)")
    ax.set_title("Interleaved scene — 'what the receiver sees'\n"
                 "(all emitters' pulses, sorted by TOA; the ESM back end must sort them back out)")
    ax.legend(loc="center right", framealpha=0.9)
    ax.set_ylim(1.5, 10.5)
    fig.tight_layout()
    save(fig, "fig_interleaved.png")


# ----------------------------------------------------------------------------
# FIG 4 — measurement noise: true vs noisy RF and PW
# ----------------------------------------------------------------------------
def fig_meas_noise():
    rng = np.random.default_rng(4)
    n = 400

    rf_true, rf_sigma = 9200.0, 4.0    # MHz
    pw_true, pw_sigma = 4.00, 0.05     # us
    rf_meas = rf_true + rng.normal(0, rf_sigma, n)
    pw_meas = pw_true + rng.normal(0, pw_sigma, n)
    idx = np.arange(n)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].scatter(idx, rf_meas, s=10, c="tab:blue", alpha=0.5, label="measured RF")
    axes[0].axhline(rf_true, color="k", lw=2, label=f"true RF = {rf_true:.0f} MHz")
    axes[0].axhspan(rf_true - rf_sigma, rf_true + rf_sigma, color="tab:blue", alpha=0.15,
                    label="+/- 1 sigma")
    axes[0].set_xlabel("pulse index n")
    axes[0].set_ylabel("RF (MHz)")
    axes[0].set_title(f"RF measurement noise  (sigma = {rf_sigma:.0f} MHz)")
    axes[0].legend(loc="upper right", fontsize=8)

    axes[1].scatter(idx, pw_meas, s=10, c="tab:red", alpha=0.5, label="measured PW")
    axes[1].axhline(pw_true, color="k", lw=2, label=f"true PW = {pw_true:.2f} us")
    axes[1].axhspan(pw_true - pw_sigma, pw_true + pw_sigma, color="tab:red", alpha=0.15,
                    label="+/- 1 sigma")
    axes[1].set_xlabel("pulse index n")
    axes[1].set_ylabel("PW (us)")
    axes[1].set_title(f"PW measurement noise  (sigma = {pw_sigma:.2f} us)")
    axes[1].legend(loc="upper right", fontsize=8)

    fig.suptitle("Per-parameter measurement noise:  x_hat = x + nu,  nu ~ N(0, sigma_x^2)",
                 fontsize=12)
    fig.tight_layout()
    save(fig, "fig_meas_noise.png")


# ----------------------------------------------------------------------------
# FIG 5 — spurious (Poisson) + dropout (Bernoulli) vs a clean train
# ----------------------------------------------------------------------------
def fig_spurious_dropout():
    rng = np.random.default_rng(5)
    win = 20_000.0  # 20 ms
    rf_ghz = 9.2

    t_clean = toas_fixed(500, win, rng)
    rf_clean = np.full_like(t_clean, rf_ghz)

    # Bernoulli dropout: keep each real pulse with prob 1 - p_d
    p_d = 0.25
    keep = rng.random(len(t_clean)) > p_d
    t_kept, rf_kept = t_clean[keep], rf_clean[keep]
    t_drop, rf_drop = t_clean[~keep], rf_clean[~keep]

    # Poisson false alarms: N_fa ~ Poisson(lambda*W), uniform TOA, RF over scene band
    lam = 3000e-6  # 3000 false alarms / second -> per-us rate
    n_fa = rng.poisson(lam * win)
    t_fa = rng.uniform(0, win, n_fa)
    rf_fa = rng.uniform(2.0, 10.0, n_fa)

    fig, axes = plt.subplots(2, 1, figsize=(9, 5.5), sharex=True)

    axes[0].scatter(t_clean / 1000.0, rf_clean, s=16, c="tab:blue", label="true pulses")
    axes[0].set_ylabel("RF (GHz)")
    axes[0].set_title("Clean pulse train (one emitter, fixed PRI)")
    axes[0].set_ylim(1.5, 10.5)
    axes[0].legend(loc="upper right", fontsize=8)

    axes[1].scatter(t_kept / 1000.0, rf_kept, s=16, c="tab:blue", label="survived")
    axes[1].scatter(t_drop / 1000.0, rf_drop, s=40, facecolors="none",
                    edgecolors="gray", label=f"dropped (p_d={p_d})")
    axes[1].scatter(t_fa / 1000.0, rf_fa, s=26, c="tab:red", marker="x",
                    label=f"false alarms (Poisson, {n_fa} added)")
    axes[1].set_xlabel("TOA (ms)")
    axes[1].set_ylabel("RF (GHz)")
    axes[1].set_title("After Bernoulli dropout + Poisson false alarms — the realistic stream")
    axes[1].set_ylim(1.5, 10.5)
    axes[1].legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    save(fig, "fig_spurious_dropout.png")


def main():
    print("Generating figures into figs/ ...")
    fig_toa_types()
    fig_pri_hist()
    fig_interleaved()
    fig_meas_noise()
    fig_spurious_dropout()
    print("Done: 5 figures written.")


if __name__ == "__main__":
    main()
