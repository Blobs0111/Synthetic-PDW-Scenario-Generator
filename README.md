# Project 1 — Synthetic PDW Scenario Generator

Generate synthetic radar pulse streams (PDWs) like the deinterleaver's reference test set, from a
config file, with a matching ground-truth table. See the full brief + background + reading in
`../../INTERN_PROJECTS.md` (Project 1).

## Run it (works today)
```
pip install -r requirements.txt
python generate.py configs/example_scene.yaml
pytest -q
```
Out of the box it generates two **fixed-PRI** emitters and writes `scene_pdw.txt` + `scene_truth.txt`.
The other PRI types are stubbed for you to implement.

## Files
- `pdw.py` — PDW record + file writers. **The output format is fixed — don't change the columns.**
- `emitters.py` — one class per PRI behavior. `FixedPRI` is a **worked example**; `StaggerPRI`,
  `JitterPRI`, `DwellPRI` are `TODO` (raise `NotImplementedError`).
- `generate.py` — CLI: config → build emitters → merge pulses → write PDW + truth. Spurious/dropout
  injection is `TODO`.
- `configs/example_scene.yaml` — sample scene (fixed emitters active; others commented until you
  implement them).
- `tests/test_emitters.py` — passing tests for `FixedPRI`, skipped `TODO` tests for the rest.

## Your task (core)
1. Implement `StaggerPRI`, `JitterPRI`, `DwellPRI` in `emitters.py` (copy the `FixedPRI` pattern).
2. Un-skip and pass their tests in `tests/test_emitters.py`.
3. Un-comment those emitters in the example config; confirm it generates.
4. Implement spurious-pulse and dropout injection in `generate.py` (the two `TODO`s).
5. Add ~5 varied scenario configs under `configs/`.

## Acceptance
- Same config + seed → identical output (deterministic).
- A new emitter can be added by editing config only.
- `pytest` is green (no skips) and covers each PRI pattern.

## Stretch
Moving emitters (bearing changes over the snapshot), scan-modulated amplitude, frequency-agile RF,
a reusable emitter-template library.
