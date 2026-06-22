from proextractor.domain.models import Arrangement, ArrangementSlideRef, Slide, Song


def test_arranged_slides_follow_references_not_physical_order() -> None:
    first = Slide(None, "first", "verse", "First")
    second = Slide(None, "second", "chorus", "Second")
    song = Song(None, "Title", "source", slides=[first, second], arrangements=[Arrangement(None, "Default", [ArrangementSlideRef("second", 0), ArrangementSlideRef("first", 1)], True)])
    assert [slide.uuid for slide in song.arranged_slides()] == ["second", "first"]

