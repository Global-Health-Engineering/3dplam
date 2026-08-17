import pytest
from tools.verify_scope import offending_reason, main


@pytest.mark.parametrize("path", [
    "cad/Petamentor2-frame.step",
    "cad/PETAMENTOR2-frame.step",
    "cad/petamentor2/frame.step",
])
def test_petamentor2_paths_are_rejected_case_insensitively(path):
    assert offending_reason(path) is not None


def test_2glam_paths_are_rejected():
    assert offending_reason("cad/2GLAM-drawing.dwg") is not None


@pytest.mark.parametrize("path", [
    "grading/rubric.pdf",
    "grading/sub/notes.txt",
])
def test_grading_directory_is_rejected(path):
    assert offending_reason(path) is not None


def test_docs_superpowers_is_rejected():
    assert offending_reason("docs/superpowers/plan.md") is not None


def test_top_level_superpowers_is_rejected():
    assert offending_reason(".superpowers/sdd/plan.md") is not None


@pytest.mark.parametrize("path", [
    "hardware/step/thing.f3d",
    "hardware/step/thing.f3z",
    "notes/slides.pptx",
    "notes/data.xlsx",
    "media/clip.mov",
    "media/clip.MOV",
    "media/clip.mp4",
    "media/photo.heic",
    "media/photo.HEIC",
])
def test_banned_extensions_are_rejected(path):
    reason = offending_reason(path)
    assert reason is not None
    assert "extension" in reason


@pytest.mark.parametrize("path", [
    "hardware/stl/base.stl",
    "docs/printing.md",
    "site/public/photos/manifold-assembled.webp",
    "README.md",
])
def test_ordinary_release_files_are_accepted(path):
    assert offending_reason(path) is None


def test_the_one_documented_video_exception_is_accepted():
    # This exact, already-reviewed asset is a processed deliverable, not
    # raw footage; see the comment above ALLOWED_EXTENSION_EXCEPTIONS in
    # tools/verify_scope.py for the full justification.
    assert offending_reason("site/public/video/base-printing-timelapse.mp4") is None


def test_a_second_video_file_is_still_rejected():
    # The exception is for one exact path, not for the extension in
    # general, proves it doesn't quietly reopen the whole video ban.
    assert offending_reason("site/public/video/another-clip.mp4") is not None


def test_main_returns_zero_when_no_offenders():
    assert main(["hardware/stl/base.stl", "README.md"]) == 0


def test_main_returns_one_when_offenders_present():
    assert main(["hardware/stl/base.stl", "grading/rubric.pdf"]) == 1
