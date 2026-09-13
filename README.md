# Synthetic PDW Scenario Generator

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

### Validation Scenarios

Dedicated validation configurations are provided for verifying individual PRI implementations:

```bash
python generate.py configs/validation_fixed.yaml
python generate.py configs/validation_stagger.yaml
python generate.py configs/validation_jitter.yaml
python generate.py configs/validation_dwell.yaml
```

These scenarios contain a single emitter with corruption effects disabled, making them useful for validating expected PRI behavior through analysis plots.

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

---

## Included Configurations

| Configuration | Description |
|--------------|-------------|
| `example_scene.yaml` | Original example scenario |
| `fixed_scene.yaml` | Multiple Fixed PRI emitters |
| `stagger_scene.yaml` | Multiple Stagger PRI emitters |
| `jitter_scene.yaml` | Multiple Jitter PRI emitters |
| `dwell_scene.yaml` | Multiple Dwell PRI emitters |
| `mixed_scene.yaml` | Combined scenario containing all supported PRI types |
| `validation_fixed.yaml` | Single-emitter Fixed PRI validation scenario |
| `validation_stagger.yaml` | Single-emitter Stagger PRI validation scenario |
| `validation_jitter.yaml` | Single-emitter Jitter PRI validation scenario |
| `validation_dwell.yaml` | Single-emitter Dwell PRI validation scenario |

New emitters using the existing PRI types can be added by modifying a configuration file without changing source code.

---

## Output Organization

Output files may be written into scenario-specific directories.

Example:

```text
outputs/
├── validation_fixed/
│   ├── validation_fixed_pdw.txt
│   └── validation_fixed_truth.txt
│
├── validation_stagger/
│   ├── validation_stagger_pdw.txt
│   └── validation_stagger_truth.txt
│
├── validation_jitter/
│   ├── validation_jitter_pdw.txt
│   └── validation_jitter_truth.txt
│
├── validation_dwell/
│   ├── validation_dwell_pdw.txt
│   └── validation_dwell_truth.txt
│
└── mixed_scene/
    ├── mixed_scene_pdw.txt
    └── mixed_scene_truth.txt
```

Output locations are defined within each configuration file and are created automatically by the generator if the specified directories do not already exist.

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

## Generating Analysis Figures

Analysis plots can be generated directly from any PDW output file.

Example:

```bash
python plot_scene.py outputs/mixed_scene/mixed_scene_pdw.txt
```

Generated figures are written to a scenario-specific directory under:

```text
figures/
```

Example:

```text
figures/
└── mixed_scene/
    ├── pri_validation.png
    ├── rf_vs_toa.png
    ├── aoa_vs_toa.png
    └── emitter_timeline.png
```

### Included Visualizations

#### PRI Validation

Interval histograms generated from dedicated validation scenarios are used to verify that each PRI implementation exhibits the expected timing behavior:

- Fixed PRI → Single interval peak
- Stagger PRI → Multiple repeating interval peaks
- Jitter PRI → Distribution centered around a mean PRI
- Dwell PRI → Multiple operating-state interval peaks

#### RF vs TOA

RF-versus-Time-of-Arrival plots visualize pulse interleaving among multiple emitters and provide a representation of the pulse stream that would be observed by an ESM receiver.

#### AoA vs TOA

AoA-versus-Time-of-Arrival visualizations provide insight into emitter bearing characteristics and can be extended to support future moving-emitter modeling.

#### Emitter Timeline

Emitter timelines display pulse arrivals grouped by emitter identifier and can be useful for debugging and scenario verification.

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
- Validation scenario configurations
- Automated analysis figure generation
- PRI validation visualizations
- RF vs TOA visualization
- Scenario-specific output directory generation

---

## Files

- `emitters.py` — Emitter implementations for Fixed, Stagger, Jitter, and Dwell PRI behaviors.
- `generate.py` — Scenario generation pipeline, including emitter construction, pulse generation, spurious pulse injection, dropout simulation, and output generation.
- `pdw.py` — PDW record definitions and file writers. The output column format should not be modified.
- `plot_scene.py` — Analysis utility for generating validation figures and visualizations from PDW outputs.
- `configs/` — Example, mixed, and validation scenario configurations.
- `outputs/` — Generated PDW and ground-truth scenario outputs.
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

The repository includes analysis and validation plots generated directly from scenario outputs.

### PRI Validation

Dedicated validation scenarios are used to verify each supported PRI implementation:

- Fixed PRI → Single dominant interval
- Stagger PRI → Repeating interval pattern
- Jitter PRI → Distribution around a configured mean
- Dwell PRI → Multiple operating-state intervals

### RF vs TOA

RF-versus-Time-of-Arrival plots visualize pulse interleaving among multiple emitters and provide a realistic representation of the data an ESM receiver would observe.

### Additional Analysis

Additional visualizations include:

- AoA vs TOA plots
- Emitter timeline plots
- Validation figures generated from dedicated PRI test scenarios

These figures are useful for verifying generator behavior, validating PRI implementations, and visualizing multi-emitter radar environments.

---

## Future Enhancements

Potential future improvements include:

- Moving emitters through changing AoA over time
- Scan-modulated amplitude
- Frequency-agile RF
- Reusable emitter-template libraries
- Enhanced emitter motion and trajectory modeling
