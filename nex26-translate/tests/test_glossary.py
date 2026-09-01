from server.glossary import Glossary


def test_apply_replaces_case_insensitive_whole_words():
    g = Glossary({"grid": "Netz", "charging point": "Ladepunkt"})
    assert g.apply("The Grid and the charging point.") == "The Netz and the Ladepunkt."
    # kein Teilwort-Ersatz
    assert g.apply("gridlock") == "gridlock"


def test_longer_entries_win():
    g = Glossary({"charging": "Laden", "charging point": "Ladepunkt"})
    assert g.apply("a charging point") == "a Ladepunkt"


def test_whisper_prompt():
    g = Glossary({"E.ON Drive": "E.ON Drive"})
    assert "E.ON Drive" in g.whisper_prompt()
    assert Glossary({}).whisper_prompt() == ""
