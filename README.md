# Project 1 — Synthetic PDW Scenario Generator

Generate synthetic radar pulse streams (PDWs) and matching ground-truth data from configurable radar emitter scenarios. The generator supports multiple PRI behaviors, measurement noise, spurious pulse injection, and pulse dropouts for testing and validation of radar pulse processing algorithms.

See `../../INTERN_PROJECTS.md` for the original project description and requirements.

---

## Running the Generator

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate a scenario using any configuration file in the `configs/` directory:

```bash
python generate.py configs/<scenario>.yaml
```

Examples:

```bash
python generate.py configs/example_scene.yaml
python generate.py configs/fixed_scene.yaml
python generate.py configs/stagger_scene.yaml
python generate.py configs/jitter_scene.yaml
python generate.py configs/dwell_scene.yaml
python generate.py configs/mixed_scene.yaml
```

Each run generates:

- A PDW file containing the simulated pulse stream.
- A ground-truth file containing the emitter information used to generate the scenario.

Output filenames are specified within each configuration file.

---

## Scenario Configuration

All scenarios are defined through YAML files located in `configs/`.

Each configuration specifies:

- Random seed
- Scenario duration
- Output file names
- Spurious pulse rate (`spurious_frac`)
- Dropout rate (`dropout_frac`)
- One or more emitters and their parameters

Example:

```yaml
emitters:
  - {type: fixed, id: 1, rf_mhz: 9200, pw_us: 0.40, aoa_deg: 45, pri_us: 516}
```

### Supported PRI Types

- `fixed` — Constant PRI
- `stagger` — Repeating PRI pattern
- `jitter` — Gaussian-distributed PRI variation
- `dwell` — Block-based PRI switching

### Included Configurations

| Configuration | Description |
|--------------|-------------|
| `example_scene.yaml` | Example scenario containing multiple PRI types and corruption effects |
| `fixed_scene.yaml` | Fixed PRI emitters only |
| `stagger_scene.yaml` | Stagger PRI emitters only |
| `jitter_scene.yaml` | Jitter PRI emitters only |
| `dwell_scene.yaml` | Dwell-switched PRI emitters only |
| `mixed_scene.yaml` | Combined scenario containing all supported PRI types |

New emitters using the existing PRI types can be added by modifying a configuration file without changing source code.

---

## Generated Outputs

### PDW File (`*_pdw.txt`)

Each scenario produces a PDW file containing:

```text
TOA_us  RF_MHz  AoA_deg  PW_us  emitter_id
```

The output may include:

- Pulses from multiple interleaved emitters
- Measurement noise
- Spurious pulses (`emitter_id = 0`)
- Pulse dropouts

### Truth File (`*_truth.txt`)

Each scenario also produces a corresponding ground-truth file containing:

- Emitter ID
- RF
- Representative PRI
- Pulse Width
- AoA
- PRI Type

These files are intended for validation and comparison against downstream processing results.

---

## Implemented Features

- Fixed PRI emitters
- Stagger PRI emitters
- Jitter PRI emitters
- Dwell-switched PRI emitters
- Measurement noise modeling
- Spurious pulse injection (false alarms)
- Pulse dropout simulation
- Config-driven scenario generation
- Ground-truth generation
- Deterministic output through seeded random number generation
- Unit test coverage for all supported PRI types

---

## Files

- `emitters.py` — Emitter implementations for Fixed, Stagger, Jitter, and Dwell PRI behaviors.
- `generate.py` — Scenario generation pipeline, including emitter construction, pulse generation, spurious pulse injection, dropout simulation, and output generation.
- `pdw.py` — PDW record definitions and file writers. The output column format should not be modified.
- `configs/` — Example and validation scenario configurations.
- `tests/test_emitters.py` — Unit tests validating behavior of all PRI emitter types.
- `figures/` — Validation and analysis plots generated from scenario outputs.

---

## Determinism

Scenario generation is deterministic. Running the same configuration with the same random seed will produce identical output files.

---

## Testing

Run the full test suite with:

```bash
pytest -q
```

The tests validate:

- Fixed PRI behavior
- Stagger PRI behavior
- Jitter PRI behavior
- Dwell PRI behavior

---

## Figures and Analysis

The repository includes validation figures generated from scenario outputs, including:

- PRI histograms for each PRI type
- Interleaved RF vs. TOA visualizations
- Additional analysis plots produced during project validation

These figures can be used to verify expected PRI behavior and visualize multi-emitter interleaved pulse streams.

---

## Stretch Goals

Potential future enhancements include:

- Moving emitters (AoA changes over time)
- Scan-modulated amplitude
- Frequency-agile RF
- Reusable emitter-template library
