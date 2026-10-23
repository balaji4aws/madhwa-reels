#!/usr/bin/env python3
"""Shared Sanskrit / Kannada / Madhwa transliteration reference list.

This is NOT a translation fix and NOT a cut-timing fix. It only addresses
TRANSLITERATION: making sure a proper noun or term that YouTube's
auto-captions render inconsistently (or wrong) in Roman script is corrected
to the one standard spelling this channel uses, every time, across every
source video.

Growing this list is a standing, ongoing task — the channel owner reviews
reels and sends corrections/additions as they're spotted. Keep asking for
more terms whenever a new source video surfaces unfamiliar names.

Structure: TERMS maps the CORRECT spelling -> info dict:
    {
        "wrong": [list of wrong variants seen in auto-captions, lowercase],
        "note": optional short gloss (who/what this is), for humans skimming
                the list -- not used by any matching logic.
    }

Usage:
    from sanskrit_terms import TERMS, correct_variants, all_correct_lower

    # get the full wrong->correct lookup (lowercase keys/values)
    fixes = correct_variants()          # {"vrishabachala": "Vrishabhachala", ...}

    # get the set of all correct spellings, lowercased, for an allowlist
    allowlist = all_correct_lower()     # {"vrishabhachala", "venkatachala", ...}
"""

TERMS = {
    "Venkatachala": {
        "wrong": [],
        "note": "The sacred hill (Tirupati) in Kali Yuga.",
    },
    "Venkateshwara": {
        "wrong": [],
        "note": "The deity of Venkatachala / Tirupati.",
    },
    "Vrishabhachala": {
        "wrong": ["vrishabachala", "vrishabachal"],
        "note": "The hill's name in Krita Yuga.",
    },
    "Vrishabhasura": {
        "wrong": ["vrishabasura"],
        "note": "The asura after whom Vrishabhachala is named.",
    },
    "Anjanachala": {
        "wrong": ["anjanachal"],
        "note": "The hill's name in Treta Yuga (named for Anjana Devi).",
    },
    "Anjana Devi": {
        "wrong": ["anjanadevi"],
        "note": "Hanuman's mother.",
    },
    # NOTE: this project standardises on "Sesha-" (not "Shesha-") for BOTH
    # the hill name and the deity name, for internal consistency -- earlier
    # reels inconsistently used "Seshachala" for the hill but "Sheshadeva"
    # for the deity. Pick one spelling family and apply it everywhere;
    # "Shesha-" variants are therefore treated as the WRONG form to fix,
    # even though both are defensible transliterations on their own.
    "Seshachala": {
        "wrong": ["sheshachala", "seshachal", "sheshachal"],
        "note": "The hill's name in Dwapara Yuga (named for the serpent deity Seshadeva).",
    },
    "Seshadeva": {
        "wrong": ["sheshadeva", "sheshadev", "seshadev"],
        "note": "The serpent deity; also 'Sesha'.",
    },
    "Vayudeva": {
        "wrong": ["vayudev"],
        "note": "The wind deity; also 'Mukhyaprana'.",
    },
    "Mukhyaprana": {
        "wrong": [],
        "note": "Another name for Vayudeva.",
    },
    "Narasimhadeva": {
        "wrong": ["narasimhadev"],
        "note": "The Lion-incarnation deity.",
    },
    "Shatananda": {
        "wrong": [],
        "note": "The sage who narrates the four names to Janaka.",
    },
    "Janaka Maharaja": {
        "wrong": [],
        "note": "King Janaka.",
    },
    "Ambarisha": {
        "wrong": [],
        "note": "The devotee-king known for dedicating all senses to God.",
    },
    "Satyatmateertha": {
        "wrong": [],
        "note": "Sri Satyatmateertha Shripadangalavaru, the discourse's speaker.",
    },
    "Shripadangalavaru": {
        "wrong": [],
        "note": "Honorific used with the speaker's name.",
    },
    "Haraye Namah": {
        "wrong": [],
        "note": "Opening words of the traditional closing dedication line.",
    },
    "Arpanamastu": {
        "wrong": ["arpanamasta"],
        "note": "Closing word of the traditional dedication formula.",
    },
    "Brahminhood": {
        "wrong": [],
        "note": "Not a proper noun, but missing from the system dictionary.",
    },
    "Utsarjana": {
        "wrong": ["utsanjana"],
        "note": "'To let go' -- ritual of setting aside Vedic study, observed "
                 "in Shravan month. YouTube auto-captions on this source "
                 "consistently mis-transcribe it as 'Utsanjana'.",
    },
    "Upakarma": {
        "wrong": [],
        "note": "'To accept/take up' -- the ritual resuming Vedic study "
                 "after Utsarjana, paired with it.",
    },
    "Shravan": {
        "wrong": [],
        "note": "The lunar month (Shravana) during which Utsarjana/Upakarma "
                 "and the Janivara/Upakarma festival are observed.",
    },
    "Janivara": {
        "wrong": [],
        "note": "Name used in this source for the Upakarma festival "
                 "(regional naming; kept as the source states it).",
    },
    "Dharmadevi": {
        "wrong": [],
        "note": "Form taken by Dharani Devi to counsel Padmavati "
                 "(venkatachala-ep06 source material).",
    },
    "Padmavati": {
        "wrong": [],
        "note": "The princess (Akasharaja's daughter) who marries "
                 "Srinivasa/Venkateshwara (venkatachala-ep06 source material).",
    },
    "Bakuladevi": {
        "wrong": [],
        "note": "The nurse/companion who helps arrange Padmavati's marriage "
                 "to Srinivasa (venkatachala-ep06 source material); appears "
                 "consistently with a single spelling in this source's "
                 "captions, same confidence level as Dharmadevi/Padmavati.",
    },
    "Srinivasa": {
        "wrong": [],
        "note": "A name of Venkateshwara / the Lord of Venkatachala; the "
                 "central figure of the Ep-06/Ep-07 wedding narrative. Used "
                 "consistently with a single spelling across both sources "
                 "(already used in venkatachala-ep06's reels via that slug's "
                 "check_reel allowlist); promoted to the shared list as a "
                 "recurring, confirmed channel spelling.",
    },
    "Vishwakarma": {
        "wrong": [],
        "note": "The divine architect/craftsman deity, standard well-known "
                 "Sanskrit proper noun with a single established spelling; "
                 "builds the wedding assembly in the venkatachala-ep07 "
                 "narrative. Not an ambiguous auto-caption artifact.",
    },
}


def correct_variants():
    """Return {wrong_lowercase: CorrectSpelling} for every known wrong form."""
    out = {}
    for correct, info in TERMS.items():
        for wrong in info.get("wrong", []):
            out[wrong.lower()] = correct
    return out


def all_correct_lower():
    """Return the set of every correct spelling's words, lowercased,
    split on spaces so multi-word terms (e.g. 'Anjana Devi') contribute
    each word individually -- matches how check_reel.py's spell-check
    tokenizes subtitle text word by word."""
    out = set()
    for correct in TERMS:
        for word in correct.split():
            out.add(word.lower())
    return out


if __name__ == "__main__":
    import sys
    print(f"{len(TERMS)} correct terms, "
          f"{sum(len(v['wrong']) for v in TERMS.values())} known-wrong variants.")
    fixes = correct_variants()
    if fixes:
        print("\nKnown wrong -> correct:")
        for wrong, correct in sorted(fixes.items()):
            print(f"  {wrong!r} -> {correct!r}")
    if "--check" in sys.argv:
        # quick self-test: every wrong variant should NOT collide with a
        # correct spelling (that would be a contradiction in the data)
        correct_lower = {c.lower() for c in TERMS}
        collisions = set(fixes) & correct_lower
        if collisions:
            print(f"\nERROR: {collisions} listed as both correct and wrong!")
            sys.exit(1)
        print("\nSelf-check OK: no correct/wrong collisions.")
