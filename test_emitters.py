import numpy as np
import pytest

from emitters import FixedPRI, StaggerPRI, JitterPRI, DwellPRI


def rng():
    return np.random.default_rng(0)


# ---- FixedPRI: worked example, should already pass ----
def test_fixed_pri_spacing():
    e = FixedPRI(pri_us=500, id=1, rf_mhz=9000, pw_us=0.5, aoa_deg=0)
    t = np.sort(e.toas(80000, rng()))
    assert len(t) > 100
    assert np.allclose(np.diff(t), 500)          # constant interval


def test_fixed_pulses_shape():
    e = FixedPRI(pri_us=500, id=7, rf_mhz=9000, pw_us=0.5, aoa_deg=0)
    p = e.pulses(80000, rng())
    assert p.shape[1] == 5
    assert np.all(p[:, 4] == 7)                  # emitter_id column


# ---- TODO: implement these classes, then delete the skip decorators ----
# @pytest.mark.skip(reason="TODO: implement StaggerPRI.toas")
def test_stagger_pattern():
    e = StaggerPRI(pattern_us=[500, 600], id=1, rf_mhz=9000, pw_us=0.5, aoa_deg=0)
    d = np.round(np.diff(np.sort(e.toas(80000, rng()))))
    assert set(np.unique(d)) <= {500, 600}       # only the two pattern intervals appear


# @pytest.mark.skip(reason="TODO: implement JitterPRI.toas")
def test_jitter_mean():
    e = JitterPRI(mean_us=500, jitter_us=50, id=1, rf_mhz=9000, pw_us=0.5, aoa_deg=0)
    d = np.diff(np.sort(e.toas(80000, rng())))
    assert abs(np.mean(d) - 500) < 20            # mean interval ~ mean PRI


# @pytest.mark.skip(reason="TODO: implement DwellPRI.toas")
def test_dwell_switches():
    e = DwellPRI(pris_us=[600, 700], dwell_us=6000, id=1, rf_mhz=9000, pw_us=0.5, aoa_deg=0)
    d = np.round(np.diff(np.sort(e.toas(80000, rng()))))
    assert {600, 700} <= set(np.unique(d))       # both PRIs appear in blocks
