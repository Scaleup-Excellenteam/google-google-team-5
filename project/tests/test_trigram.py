import pytest
from project.trigram import _trigrams, _normalize

def test_normalize() :
    assert _normalize("Hello, World!") == "hello world"

def test_normalize_two() :
    assert _normalize("how     ArE ^$%# YOu     ?") == "how are you"

def test_trigram_two_letters():
    result = list(_trigrams("ab"))
    assert result==["ab"] # exactly one trigram.

def test_trigram_three_letters():
    result = list(_trigrams("abc"))
    assert result==["abc"] # exactly one trigram.

def test_trigram_long_input():
    result = list(_trigrams("hello"))
    assert result==["hel", "ell", "llo"]

def test_trigram_long_input_two():
    result = list(_trigrams("this is"))
    assert result==["thi", "his", "is ", "s i", " is"]
