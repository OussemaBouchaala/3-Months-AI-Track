# Tunisian text mixes scripts and languages in one sentence:
#   "Appartement S+2 للبيع في Sahloul, prix 250 mille"   or in Arabizi: "3andi chi9a fi Sousse, 9adech el kra?"
# Detect what you're looking at before you normalize, tokenize or pick a prompt.
import re

FR_WORDS = {"le", "la", "les", "de", "des", "du", "et", "à", "pour", "avec", "est", "une", "un", "prix", "vendre", "louer", "chambre"}
EN_WORDS = {"the", "and", "for", "with", "is", "a", "an", "of", "to", "price", "sale", "rent", "room", "flat", "apartment"}
# Arabizi (Latin letters + digits for Arabic sounds), Tunisian usage
ARABIZI = {"2": "ء", "3": "ع", "5": "خ", "7": "ح", "9": "ق"}


def script_of(token):
    """"arabic" if it contains an Arabic letter (ء-ي), else "digit" if it is only digits,
    else "latin" if it contains a-z letters (any case, accents allowed: use str.isalpha on a char), else "other"."""
    # TODO
    ...


def script_ratio(text):
    """Share of word tokens (re.findall(r"\w+")) per script, e.g. {"arabic": 0.5, "latin": 0.5}. Scripts with 0 are omitted."""
    # TODO
    ...


def is_arabizi(token):
    """A Latin word that uses at least one of the ARABIZI digits as a letter: it has a letter AND one of 2 3 5 7 9.
    "3andi", "chi9a", "7ata" -> True. "S+2"'s token "2", "2026", "sousse" -> False."""
    # TODO
    ...


def detect_lang(text):
    """"ar" if at least half the word tokens are Arabic script or Arabizi, OR if there are 2+ Arabizi tokens
    and they outnumber the French and English word hits together (Arabizi mixes in plain words like "fi", "el").
    Otherwise compare lowercase token hits in FR_WORDS vs EN_WORDS: "fr" if more French, "en" if more English,
    "fr" on a tie (most Tunisian listings in Latin script are French)."""
    # TODO
    ...


def split_runs(text):
    """Split into consecutive runs of the same script, ignoring digits and "other" tokens:
    "شقة للبيع Appartement S+2 في سوسة" -> [("arabic", "شقة للبيع"), ("latin", "Appartement S"), ("arabic", "في سوسة")]
    Join tokens of a run with one space."""
    # TODO
    ...


if __name__ == "__main__":
    for t in ["Appartement S+2 للبيع في Sahloul, prix 250 mille",
              "3andi chi9a fi Sousse, 9adech el kra?",
              "Flat for rent near the beach, 3 rooms",
              "شقة للكراء قرب البحر"]:
        print(detect_lang(t), script_ratio(t), split_runs(t), sep="  |  ")
