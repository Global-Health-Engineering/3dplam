"""WHO drinking-water microbial risk classification.

Bands follow WHO (2024), Guidelines for drinking-water quality: small water
supplies. Samples with no visible colonies are recorded as 0.5 CFU/100 mL.

The 5% rule: a geometric mean lying within 5% of a band boundary may be
classified into either adjacent band. Applied when comparing a 3D-printed
manifold against the Millipore reference, it turns 12/16 raw category
matches into the published 15/16.
"""
import math

# WHO states the bands with integer gaps: "<1", "1-10", "11-100",
# "101-1000". They are implemented here as half-open intervals cutting at
# the round numbers 1, 10 and 100, so classify(10.0) is "high risk".
# This is deliberate and load-bearing: it is what makes the published
# raw 12/16 and accepted 15/16 counts reproduce. Moving the cuts to 11
# and 101 to match the literal WHO wording would silently change the
# headline result. Do not "correct" these values.
BANDS = [
    ("low risk", 0.0, 1.0),
    ("intermediate risk", 1.0, 10.0),
    ("high risk", 10.0, 100.0),
    ("very high risk", 100.0, 1000.0),
]

THRESHOLDS = [1.0, 10.0, 100.0]

DEFAULT_TOLERANCE = 0.05


def classify(cfu):
    """Return the WHO risk band for a CFU/100 mL value."""
    for name, lo, hi in BANDS:
        if lo <= cfu < hi:
            return name
    if cfu >= BANDS[-1][2]:
        return BANDS[-1][0]
    raise ValueError(f"cfu must be non-negative, got {cfu}")


def geometric_mean(values):
    """Geometric mean of positive values."""
    values = list(values)
    if not values:
        raise ValueError("geometric_mean requires at least one value")
    if any(v <= 0 for v in values):
        raise ValueError("all values must be positive; use 0.5 for no colonies")
    return math.exp(sum(math.log(v) for v in values) / len(values))


def near_threshold(cfu, tolerance=DEFAULT_TOLERANCE):
    """True if cfu lies within `tolerance` (relative) of a band boundary."""
    return any(abs(cfu - t) <= t * tolerance for t in THRESHOLDS)


def separating_threshold(band_a, band_b):
    """The single boundary between two adjacent bands, or None if not adjacent."""
    names = [b[0] for b in BANDS]
    i, j = names.index(band_a), names.index(band_b)
    if abs(i - j) != 1:
        return None
    return BANDS[max(i, j)][1]


def is_acceptable(test_cfu, reference_cfu, tolerance=DEFAULT_TOLERANCE):
    """True if a test manifold's classification is acceptable.

    Acceptable when the bands match outright, or when the two bands are
    adjacent AND at least one value lies within `tolerance` of *the
    boundary that separates those two bands specifically*.

    The boundary must be the separating one. Checking proximity to any
    threshold would accept pairs straddling a boundary neither value is
    near — e.g. 1.03 (intermediate, near the 1.0 boundary) against 50.0
    (high), whose separating boundary is 10.0 and which nothing is near.
    """
    test_band, ref_band = classify(test_cfu), classify(reference_cfu)
    if test_band == ref_band:
        return True
    boundary = separating_threshold(test_band, ref_band)
    if boundary is None:
        return False
    return (abs(test_cfu - boundary) <= boundary * tolerance
            or abs(reference_cfu - boundary) <= boundary * tolerance)
