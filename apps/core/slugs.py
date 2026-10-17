"""Slug из заголовка: ru — транслит, en — slugify, zh — pinyin + slugify (SPEC.md, 4.1)."""
from pypinyin import lazy_pinyin
from slugify import slugify

SLUG_MAX_LENGTH = 100


def make_slug(text, lang):
    if not text:
        return None
    if lang == "zh":
        text = " ".join(lazy_pinyin(text))
    return slugify(text, max_length=SLUG_MAX_LENGTH, word_boundary=True) or None
