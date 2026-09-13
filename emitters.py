"""Emitter models — one class per PRI behavior.

Each emitter turns into a pulse train. The only method you must implement per class is
`toas(t_end_us, rng)`, which returns the emitter's pulse arrival times (µs) over [0, t_end_us].
The base class adds RF/PW/AoA (with measurement noise) to make full PDW rows.

`FixedPRI` is a WORKED EXAMPLE. Implement `StaggerPRI`, `JitterPRI`, `DwellPRI` the same way.
"""
import numpy as np


class Emitter:
    def __init__(self, id, rf_mhz, pw_us, aoa_deg,
                 rf_jit=0.5, pw_jit=0.02, aoa_jit=5.0, aoa_rate_deg_per_s = 0.0):
        self.id = id
        self.rf = rf_mhz
        self.pw = pw_us
        self.aoa = aoa_deg
        self.aoa_rate = aoa_rate_deg_per_s
        self.rf_jit = rf_jit
        self.pw_jit = pw_jit
        self.aoa_jit = aoa_jit

    def toas(self, t_end_us, rng):
        raise NotImplementedError

    def pulses(self, t_end_us, rng):
        """Return (N,5) [toa_us, rf_mhz, aoa_deg, pw_us, emitter_id]."""
        t = np.asarray(self.toas(t_end_us, rng), dtype=float)
        t_sec = t * 1e-6
        n = len(t)
        rf = self.rf + rng.normal(0, self.rf_jit, n)
        pw = self.pw + rng.normal(0, self.pw_jit, n)
        aoa_true = self.aoa + self.aoa_rate * t_sec
        aoa = aoa_true + rng.normal(0, self.aoa_jit, n)
        return np.column_stack([t, rf, aoa, pw, np.full(n, self.id)])


class FixedPRI(Emitter):
    """Constant PRI.  WORKED EXAMPLE — copy this shape for the others."""
    def __init__(self, pri_us, **kw):
        super().__init__(**kw)
        self.pri = pri_us

    def toas(self, t_end_us, rng):
        t0 = rng.uniform(0, self.pri)               # random start phase
        return np.arange(t0, t_end_us, self.pri)


class StaggerPRI(Emitter):
    """Repeating pattern of PRIs, e.g. [520, 560, 600] cycled forever.

    TODO: build the TOA sequence by cumulatively summing the cycled `pattern` until t_end.
    Hint: start at a random phase, then repeatedly add pattern[i % len(pattern)].
    """
    def __init__(self, pattern_us, **kw):
        super().__init__(**kw)
        self.pattern = list(pattern_us)

    def toas(self, t_end_us, rng):
        # raise NotImplementedError("TODO: implement staggered PRI")

        # Convert pattern list to NumPy Array
        pattern = np.asarray(self.pattern, dtype = float)
        M = len(pattern)

        # Randomize start time
        t0 = rng.uniform(0, pattern[0])

        # Calculate the number of indexes needed to reach t_end_us (Over-generates indexes with ceil and adding M to safely reach t_end_us)
        num_indexes = int(np.ceil(t_end_us / np.mean(pattern)) + M)

        # Create list of PRIs from num_indexes
        pris = pattern[np.arange(num_indexes) % M]

        # Create list of TOAs from cumulative sum of PRIs, prepends random start time
        toas = t0 + np.concatenate([[0.0], np.cumsum(pris)])

        # Return TOAs strictly within t_end_us limit
        return toas[toas < t_end_us]

class JitterPRI(Emitter):
    """Mean PRI with random jitter — each interval ~ N(mean, jitter).

    TODO: generate intervals from rng.normal(mean, jitter), cumulative-sum to TOAs, stop at t_end.
    """
    def __init__(self, mean_us, jitter_us, **kw):
        super().__init__(**kw)
        self.mean = mean_us
        self.jitter = jitter_us

    def toas(self, t_end_us, rng):
        # raise NotImplementedError("TODO: implement jittered PRI")
        # Overestimate n to comfortably reach t_end_us
        n = int(t_end_us / self.mean * 1.5) + 10

        # Collect n samples of Gaussian values based on mean and jitter
        intervals = rng.normal(self.mean, self.jitter, n)

        # Adjust intervals to prevent negative values
        intervals = np.clip(intervals, 1e-6, None)

        # Randomize start time
        t0 = rng.uniform(0, self.mean)

        # Create list of TOAs, adds t0 to list values (as offset for other pulses rather than pulse arrival itself)
        toas = t0 + np.cumsum(intervals)

        # Return TOAs strictly within t_end_us limit
        return toas[toas < t_end_us]

class DwellPRI(Emitter):
    """Dwell-switched / agile — hold PRI A for `dwell_us`, switch to B, etc., cycling `pris`.

    TODO: within each dwell block emit at the current PRI; advance to the next PRI after dwell_us.
    """
    def __init__(self, pris_us, dwell_us, **kw):
        super().__init__(**kw)
        self.pris = list(pris_us)
        self.dwell = dwell_us

    def toas(self, t_end_us, rng):
        # raise NotImplementedError("TODO: implement dwell-switched PRI")
        # Randomize start time
        t = rng.uniform(0, self.pris[0])

        # Initialize counter for tracking time of current dwell block
        t_current_block = t

        # Initialize current PRI index
        b = 0

        # Initialize list for TOAs (for dynamic size)
        toas = []

        while(t < t_end_us):
            # Appends current t
            toas.append(t)

            # Adds dwell block's corresponding PRI to t
            t += self.pris[b % len(self.pris)]

            # Checks if current dwell block is over
            if(t - t_current_block >= self.dwell):
                # Updates PRI index b and t_current_block to current time
                b += 1
                t_current_block = t

        # Convert toas to NumPy array for easy return indexing
        toas = np.asarray(toas)
        return toas[toas < t_end_us]

# name -> class, used by the config loader in generate.py
TYPES = {
    "fixed": FixedPRI,
    "stagger": StaggerPRI,
    "jitter": JitterPRI,
    "dwell": DwellPRI,
}
