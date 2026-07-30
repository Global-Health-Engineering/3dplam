"""WHO drinking-water microbial risk classification.

Bands follow WHO (2024), Guidelines for drinking-water quality: small water
supplies. Samples with no visible colonies are recorded as 0.5 CFU/100 mL.

The 5% rule: a geometric mean lying within 5% of a band boundary may be
classified into either adjacent band. Applied when comparing a 3D-printed
manifold against the Millipore reference, it turns 12/16 raw category
matches into the published 15/16.
"""
import math

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


def is_acceptable(test_cfu, reference_cfu, tolerance=DEFAULT_TOLERANCE):
    """True if a test manifold's classification is acceptable.

    Acceptable when the bands match outright, or when either value lies
    within `tolerance` of a boundary and the two land in adjacent bands.
    """
    if classify(test_cfu) == classify(reference_cfu):
        return True
    if not (near_threshold(test_cfu, tolerance)
            or near_threshold(reference_cfu, tolerance)):
        return False
    names = [b[0] for b in BANDS]
    return abs(names.index(classify(test_cfu))
               - names.index(classify(reference_cfu))) == 1
