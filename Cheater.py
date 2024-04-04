from Corpus import Corpus
from collections import Counter

from guesser import EntropyCalculator


def find_all_matches(word, c):
    matches = []
    for i in range(len(word)):
        if word[i] == c:
            matches.append(i)
    return matches


def is_possible(word, unmatched, match_at_loc, match_at_noloc):
    if set(word).intersection(unmatched):
        return False

    for m in match_at_loc:
        if word[m[1]] != m[0]:
            return False

    for nmal in match_at_noloc:
        indices = find_all_matches(word, nmal[0])
        if indices == [] or nmal[1] in indices:
            return False

    return True


def get_possibilities(guesses):
    solutions = Corpus.get_real_solutions()

    unmatched = set(guesses["unmatched"])

    possibilities = []
    for potential in solutions:
        if is_possible(potential, unmatched, guesses["mal"], guesses["nmal"]):
            possibilities.append(potential)

    return possibilities


if __name__ == "__main__":
    guesses = {
        "mal": [("l", 1), ("a", 2)],
        "nmal": [("t", 3)],
        "unmatched": "se",
    }

    possibilities = get_possibilities(guesses)
    print(possibilities)

    c = Counter([c for word in possibilities for c in word])
    # Corpus.get_real_solutions())
    ec = EntropyCalculator(possibilities, possibilities)
    ec.eliminates()

    ec = EntropyCalculator(possibilities, Corpus.get_real_solutions())
    ec.eliminates()
