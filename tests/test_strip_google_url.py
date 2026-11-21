import re
import pytest
from devi.operator.deep_cloner import clean_cloned_caption
from tg_kindsync_pro import apply_clean_rules

def test_clean_google_redirects_and_promo_links():
    raw = (
        "Join [Medical Verse](https://t.me/) For more\n"
        "//www.google.com/url?sa=t&source=web&rct=j&opi=85673748&url=&ved=2ahUKEwiclv3k06iRAxUTlJUCHczQM0UQFnoECA4QAQ&usg=AOvVaw1mgHhHFpHrOVr-HIFqBTgP)://www.google.com/url?sa=t&source=web&rct=j&opi=97423376&url=&ved=2ahUKEwiclv3k06iRAxUTlJUCHczQM0UQFnoECA4QAQ&usg=AOvVaw1mgHhHFpHrOVr-HIFqBTgP)\n"
        "Title: 01. General Anatomy Introduction\n"
    )

    cleaned = clean_cloned_caption(raw, topic_title="General Anatomy")
    assert "Medical Verse" not in cleaned
    assert "google.com" not in cleaned
    assert "//www" not in cleaned
    assert "Title: 01. General Anatomy Introduction" in cleaned
    assert "Kind Doctor & Team" in cleaned


def test_clean_atf_and_verse_variations():
    """Verify atf, @verse medical, @verse and all case variations are stripped cleanly."""
    raw = (
        "Title: Pathology Neoplasia Part 1\n"
        "Download atf files from ATF portal or Atf study hub.\n"
        "Check @atf, @ATF and @Atf with #atf #ATF.\n"
        "Follow @verse medical and @VERSE MEDICAL and @verse_medical.\n"
        "Visit verse medical, Verse Medical or VERSE MEDICAL today.\n"
        "Also join @verse and #verse.\n"
        "Core study notes attached."
    )
    cleaned = clean_cloned_caption(raw, is_media=True)
    # Check that promotional words are gone
    assert "@atf" not in cleaned
    assert "@ATF" not in cleaned
    assert "@Atf" not in cleaned
    assert "#atf" not in cleaned
    assert "#ATF" not in cleaned
    assert "@verse medical" not in cleaned
    assert "@VERSE MEDICAL" not in cleaned
    assert "@verse_medical" not in cleaned
    assert "@verse" not in cleaned
    # Educational content preserved
    assert "Title: Pathology Neoplasia Part 1" in cleaned
    assert "Core study notes attached." in cleaned
    assert "Kind Doctor & Team" in cleaned

    # Also test in tg_kindsync_pro.apply_clean_rules
    tg_cleaned = apply_clean_rules("Pathology atf ATF Atf @atf #atf @verse medical @verse notes")
    assert "atf" not in tg_cleaned.lower()
    assert "verse" not in tg_cleaned.lower()
    assert "Pathology" in tg_cleaned
    assert "notes" in tg_cleaned



def test_clean_medical_verse_exact_user_sample():
    raw = (
        "Join [Medical Verse](https://t.me/verse_medical) For more\n"
        "[medicalverse.in](https://www.google.com/url?sa=t&source=web&rct=j&opi=97423376&url=https://medicalverse.in/&ved=2ahUKEwiclv3k06iRAxUTlJUCHczQM0UQFnoECA4QAQ&usg=AOvVaw1mgHhHFpHrOVr-HIFqBTgP)\n\n"
        "Title: Pharmacology CVS Lecture 01\n"
        "Essential concepts in beta blockers."
    )
    cleaned = clean_cloned_caption(raw, is_media=True)
    assert "Medical Verse" not in cleaned
    assert "verse_medical" not in cleaned
    assert "medicalverse" not in cleaned
    assert "google.com" not in cleaned
    assert "Title: Pharmacology CVS Lecture 01" in cleaned
    assert "Essential concepts in beta blockers." in cleaned
    assert "Kind Doctor & Team" in cleaned


