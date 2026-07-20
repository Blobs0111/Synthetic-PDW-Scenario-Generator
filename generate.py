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
    # TODO (core): inject dropouts — randomly delete cfg['dropout_frac'] of the pulses.

    write_pdw(cfg.get("out_pdw", "scene_pdw.txt"), pulses)
    write_truth(cfg.get("out_truth", "scene_truth.txt"), truth)
    print(f"wrote {len(pulses)} pulses from {len(emitters)} emitters "
          f"-> {cfg.get('out_pdw','scene_pdw.txt')}, {cfg.get('out_truth','scene_truth.txt')}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "configs/example_scene.yaml")
