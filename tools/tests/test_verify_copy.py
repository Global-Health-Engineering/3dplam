import pytest
from tools.verify_copy import scan_file, find_files, main


def write(path, text):
    path.write_text(text)
    return str(path)


def test_scan_file_detects_banned_phrase_case_insensitively(tmp_path):
    p = write(tmp_path / "page.md", "This device REPLACES THE MILLIPORE unit.\n")
    hits = scan_file(p)
    assert len(hits) == 1
    line_no, phrase, line_text = hits[0]
    assert line_no == 1
    assert phrase == "replaces the millipore"


def test_scan_file_reports_the_correct_line_number(tmp_path):
    p = write(tmp_path / "page.md", "line one is fine\nline two is a drop-in replacement\nline three too\n")
    hits = scan_file(p)
    assert [h[0] for h in hits] == [2]


def test_scan_file_finds_multiple_phrases_on_one_line(tmp_path):
    p = write(tmp_path / "page.md", "It replaces the Millipore and is equivalent to the Millipore.\n")
    hits = scan_file(p)
    phrases = {h[1] for h in hits}
    assert phrases == {"replaces the millipore", "equivalent to the millipore"}


def test_scan_file_returns_empty_for_clean_text(tmp_path):
    p = write(tmp_path / "page.md", "Validated against the Millipore EZ-Fit as the reference instrument.\n")
    assert scan_file(p) == []


def test_find_files_only_matches_known_text_suffixes(tmp_path):
    write(tmp_path / "page.md", "clean")
    write(tmp_path / "image.png", "not text, ignored by suffix filter")
    found = find_files([str(tmp_path / "*")])
    assert found == [str(tmp_path / "page.md")]


def test_main_returns_zero_when_clean(tmp_path):
    p = write(tmp_path / "page.md", "an alternative route to the same measurement\n")
    assert main([p]) == 0


def test_main_returns_one_when_banned_phrase_present(tmp_path):
    p = write(tmp_path / "page.md", "a drop-in replacement for the lab unit\n")
    assert main([p]) == 1


def test_main_returns_one_when_no_files_matched(tmp_path):
    assert main([str(tmp_path / "nothing-here-*.md")]) == 1
