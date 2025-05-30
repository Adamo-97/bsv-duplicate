# test/unit/test_detect_duplicates.py

import pytest
from src.util.detector import detect_duplicates

# Helpers to build sample .bib data
ENTRY_TMPL = "@article{{{key}, title={{test}}, year={{2024}}{doi_part}}}"
def build_entry(key: str, doi: str | None = None) -> str:
    doi_part = f", doi={{{doi}}}" if doi else ""
    return ENTRY_TMPL.format(key=key, doi_part=doi_part)

def make_bibliography(entries: list[str]) -> str:
    return "\n\n".join(entries) + "\n"

def keys_of(dups: list) -> list[str]:
    return [a.key for a in dups]

@pytest.mark.unit
def test_tc1_empty_input_raises_value_error():
    # TC1: zero articles → ValueError
    with pytest.raises(ValueError):
        detect_duplicates("")

@pytest.mark.unit
def test_tc2_single_entry_raises_value_error():
    # TC2: one article → should raise ValueError
    bib = make_bibliography([build_entry("A")])
    with pytest.raises(ValueError):
        detect_duplicates(bib)

@pytest.mark.unit
def test_tc3_two_diff_keys_no_doi():
    # TC3: two entries, different keys, no DOIs → no duplicates
    bib = make_bibliography([build_entry("A"), build_entry("B")])
    assert keys_of(detect_duplicates(bib)) == []

@pytest.mark.unit
def test_tc4_two_same_key_no_doi():
    # TC4: two entries, same key, no DOIs → one duplicate
    bib = make_bibliography([build_entry("X"), build_entry("X")])
    assert keys_of(detect_duplicates(bib)) == ["X"]

@pytest.mark.unit
def test_tc5_same_key_same_doi():
    # TC5: same key & same DOI → one duplicate
    bib = make_bibliography([
        build_entry("K", "10.1000/xyz"),
        build_entry("K", "10.1000/xyz"),
    ])
    assert keys_of(detect_duplicates(bib)) == ["K"]

@pytest.mark.unit
def test_tc6_same_key_diff_doi():
    # TC6: same key, different DOIs → no duplicates per spec
    bib = make_bibliography([
        build_entry("K", "10.1000/xyz"),
        build_entry("K", "10.1000/abc"),
    ])
    assert keys_of(detect_duplicates(bib)) == []

@pytest.mark.unit
def test_tc7_diff_key_same_doi():
    # TC7: different keys, same DOI → no duplicates
    bib = make_bibliography([
        build_entry("A", "10.1000/xyz"),
        build_entry("B", "10.1000/xyz"),
    ])
    assert keys_of(detect_duplicates(bib)) == []

@pytest.mark.unit
def test_tc8_one_doi_same_key():
    # TC8: one DOI only, same key → one duplicate
    bib = make_bibliography([
        build_entry("Z", "10.1000/xyz"),
        build_entry("Z"),
    ])
    assert keys_of(detect_duplicates(bib)) == ["Z"]

@pytest.mark.unit
def test_tc9_three_same_key_no_doi():
    # TC9: three entries all same key, no DOIs → two duplicates
    bib = make_bibliography([
        build_entry("X"),
        build_entry("X"),
        build_entry("X"),
    ])
    assert keys_of(detect_duplicates(bib)) == ["X", "X"]

# Notes:
# - TC2, TC6, and TC9 will fail under the current implementation:
#     * TC2: the code only raises ValueError for zero entries, not one.
#     * TC6: the code treats same-key but different-DOI entries as duplicates.
#     * TC9: the code returns three duplicates for three identical keys rather than two.
# - These failures highlight mismatches between the code and the requirements spec.
