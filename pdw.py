"""PDW record + file I/O.

The output format matches the deinterleaver's input: a whitespace-separated
text file, one row per pulse, time-sorted:

    TOA_us   RF_MHz   AoA_deg   PW_us   emitter_id

DO NOT change the writer columns/order — downstream tools depend on it.
"""
import numpy as np

COLUMNS = ["toa_us", "rf_mhz", "aoa_deg", "pw_us", "emitter_id"]


def write_pdw(path, pulses):
    """Write an (N,5) array [toa_us, rf_mhz, aoa_deg, pw_us, emitter_id] (any order in);
    output is time-sorted and space-separated."""
    p = np.asarray(pulses, dtype=float)
    p = p[np.argsort(p[:, 0])]  # sort by TOA
    np.savetxt(path, p, fmt=["%.3f", "%.1f", "%.2f", "%.3f", "%d"])
    return path


def write_truth(path, rows):
    """Ground-truth table. `rows` = list of dicts with id, rf, pri, pw, aoa, type."""
    with open(path, "w") as f:
        f.write("id rf_mhz pri_us pw_us aoa_deg type\n")
        for r in rows:
            f.write(f"{r['id']} {r['rf']:.1f} {r['pri']:.2f} {r['pw']:.3f} {r['aoa']:.2f} {r['type']}\n")
    return path
