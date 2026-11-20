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

