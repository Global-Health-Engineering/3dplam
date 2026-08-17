import pytest
from tools.risk import classify, geometric_mean, near_threshold, is_acceptable, separating_threshold


@pytest.mark.parametrize("cfu,expected", [
    (0.5, "low risk"),
    (0.99, "low risk"),
    (1.0, "intermediate risk"),
    (9.97, "intermediate risk"),
    (10.0, "high risk"),
    (62.07, "high risk"),
    (100.0, "very high risk"),
    (103.17, "very high risk"),
])
def test_classify_assigns_who_bands(cfu, expected):
    assert classify(cfu) == expected


def test_geometric_mean_matches_published_values():
    assert geometric_mean([25, 27, 31]) == pytest.approx(27.56, abs=0.01)
    assert geometric_mean([48, 56, 50]) == pytest.approx(51.22, abs=0.01)
    assert geometric_mean([0.5, 0.5, 0.5]) == pytest.approx(0.5, abs=0.01)


def test_near_threshold_detects_boundary_proximity():
    assert near_threshold(9.97) is True       # just under 10
    assert near_threshold(103.17) is True     # just over 100
    assert near_threshold(3.66) is False      # mid-band
    assert near_threshold(27.56) is False


def test_sample_4_abs_is_forgiven():
    """ABS 9.97 (intermediate) vs Millipore 11.05 (high), boundary case."""
    assert classify(9.97) != classify(11.05)
    assert is_acceptable(9.97, 11.05) is True


def test_sample_5_both_manifolds_forgiven():
    """Millipore 103.17 sits within 5% of the 100 boundary."""
    assert is_acceptable(62.07, 103.17) is True
    assert is_acceptable(50.78, 103.17) is True


def test_sample_7_rpet_is_not_forgiven():
    """3.66 (intermediate) vs 90.42 (high), nowhere near a boundary."""
    assert is_acceptable(3.66, 90.42) is False


def test_exact_category_match_is_always_acceptable():
    assert is_acceptable(27.56, 29.55) is True
    assert is_acceptable(0.5, 0.5) is True


def test_headline_result_is_fifteen_of_sixteen():
    """The published claim, reproduced end to end."""
    pairs = [
        (27.56, 29.55), (22.68, 29.55),      # sample 1
        (51.22, 55.96), (38.90, 55.96),      # sample 2
        (12.21, 16.19), (10.49, 16.19),      # sample 3
        (12.06, 11.05), (9.97, 11.05),       # sample 4
        (62.07, 103.17), (50.78, 103.17),    # sample 5
        (3.42, 5.24), (1.82, 5.24),          # sample 6
        (3.66, 90.42), (23.45, 90.42),       # sample 7
        (0.50, 0.50), (0.50, 0.50),          # sample 8
    ]
    assert len(pairs) == 16
    raw = sum(1 for t, r in pairs if classify(t) == classify(r))
    accepted = sum(1 for t, r in pairs if is_acceptable(t, r))
    assert raw == 12, "raw category matching"
    assert accepted == 15, "after the 5% threshold rule"


def test_proximity_must_be_to_the_separating_boundary():
    """1.03 is near the 1.0 threshold, but 1.0 is not what separates it from 50."""
    assert classify(1.03) == "intermediate risk"
    assert classify(50.0) == "high risk"
    assert is_acceptable(1.03, 50.0) is False


def test_separating_threshold_picks_the_shared_boundary():
    assert separating_threshold("intermediate risk", "high risk") == 10.0
    assert separating_threshold("high risk", "very high risk") == 100.0
    assert separating_threshold("low risk", "intermediate risk") == 1.0
    assert separating_threshold("low risk", "high risk") is None


def test_band_cut_points_are_at_round_numbers():
    """Pins the convention the headline result depends on."""
    assert classify(10.0) == "high risk"
    assert classify(9.999) == "intermediate risk"
    assert classify(100.0) == "very high risk"
    assert classify(99.999) == "high risk"
