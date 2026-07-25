"""Scenario generator CLI.

    python generate.py configs/example_scene.yaml

Reads a scene config, builds emitters, generates + merges their pulse trains, and writes a
PDW file + a ground-truth table. Spurious-pulse and dropout injection are left as TODOs.
"""
import sys
import numpy as np
import yaml

from emitters import TYPES
from pdw import write_pdw, write_truth

# Create spurious pulses/false alarms to inject
def inject_spurious(spurious_frac, t_end, pulses, rng):
    # Calculate number of spurious pulses to inject
    n_fa = round(spurious_frac * len(pulses))

    # Generate random TOAs for n_fa spurious pulses
    toa = rng.uniform(0, t_end, n_fa)

    # Find range (max/min) of RFs from list of pulses
    rf_max = pulses[:, 1].max()
    rf_min = pulses[:, 1].min()

    # Generate random RFs for n_fa spurious pulses
    rf = rng.uniform(rf_min, rf_max, n_fa)

    # Find range (max/min) of PWs from list of pulses
    pw_max = pulses[:, 3].max()
    pw_min = pulses[:, 3].min()

    # Generate random PWs for n_fa spurious pulses
    pw = rng.uniform(pw_min, pw_max, n_fa)

    # Generate random AoAs for n_fa spurious pulses
    aoa = rng.uniform(-180, 180, n_fa)

    # Give every spurious pulse id of 0
    eid = np.zeros(n_fa)

    # Combine and return spurious pulses
    return np.column_stack([toa, rf, aoa, pw, eid])

# Simulates dropout (Bernoulli Thinning)
def apply_dropout(pulses, p_d, rng):
    # Generate len(pulses) random numbers between 0 and 1, if exceeds p_d, pulse is kept
    keep = rng.random(len(pulses)) > p_d

    # Performs boolean masking numpy feature, removes pulses which didn't exceed p_d
    return pulses[keep]

def build(cfg):
    """Turn each config emitter dict into an Emitter object (keys must match constructor kwargs)."""
    emitters = []
    for e in cfg["emitters"]:
        params = {k: v for k, v in e.items() if k != "type"}
        obj = TYPES[e["type"]](**params)
        obj._kind = e["type"]
        emitters.append(obj)
    return emitters


def main(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    rng = np.random.default_rng(cfg.get("seed", 0))
    t_end = cfg.get("duration_ms", 80) * 1000.0

    emitters = build(cfg)
    all_pulses, truth = [], []
    for e in emitters:
        p = e.pulses(t_end, rng)
        all_pulses.append(p)
        toa = np.sort(p[:, 0])
        pri = float(np.median(np.diff(toa))) if len(toa) > 1 else 0.0  # representative PRI
        truth.append({"id": e.id, "rf": e.rf, "pri": pri, "pw": e.pw, "aoa": e.aoa, "type": e._kind})

    pulses = np.vstack(all_pulses)

    # TODO (core): inject spurious pulses — cfg['spurious_frac'] * len(pulses) extra rows with
    #   uniform-random TOA in [0,t_end], RF/PW drawn across the scene's range, emitter_id = 0.
    spurious_pulses = inject_spurious(cfg['spurious_frac'], t_end, pulses, rng)

    # Merges spurious pulses into scene
    pulses = np.vstack([pulses, spurious_pulses])

    # TODO (core): inject dropouts — randomly delete cfg['dropout_frac'] of the pulses.
    pulses = apply_dropout(pulses, cfg['dropout_frac'], rng)

    write_pdw(cfg.get("out_pdw", "scene_pdw.txt"), pulses)
    write_truth(cfg.get("out_truth", "scene_truth.txt"), truth)
    print(f"wrote {len(pulses)} pulses from {len(emitters)} emitters "
          f"-> {cfg.get('out_pdw','scene_pdw.txt')}, {cfg.get('out_truth','scene_truth.txt')}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "configs/example_scene.yaml")
