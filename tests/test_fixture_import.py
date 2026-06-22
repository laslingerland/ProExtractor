import os
from pathlib import Path

import pytest

from proextractor.adapters.propresenter import ProPresenterLegacyProImporter


FIXTURE_PATH = os.environ.get("PROEXTRACTOR_REAL_PRO_FIXTURE")
FIXTURE = Path(FIXTURE_PATH) if FIXTURE_PATH else None


@pytest.mark.skipif(FIXTURE is None or not FIXTURE.exists(), reason="real .pro fixture is unavailable")
def test_real_fixture_recovers_sections_text_and_explicit_arrangement() -> None:
    assert FIXTURE is not None
    song = ProPresenterLegacyProImporter().import_from_path(FIXTURE)[0]
    assert song.title == "No One Like The Lord (We crown you)"
    assert {section.name for section in song.sections} >= {"Verse 1", "Chorus 1", "Instrumental"}
    assert any(slide.sung_text == "Worthy is the Lamb" and slide.translation == "Waardig is het Lam" for slide in song.slides)
    assert song.default_arrangement() is not None
    assert song.default_arrangement().name == "20260315"
    assert len(song.arranged_slides()) > 10
