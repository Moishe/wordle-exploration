import json
import Corpus
from collections import Counter

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
    solutions = Corpus.Corpus.get_real_solutions()

    unmatched = set(guesses["unmatched"])

    possibilities = []
    for potential in solutions:
        if is_possible(potential, unmatched, guesses["mal"], guesses["nmal"]):
            possibilities.append(potential)

    return possibilities


if __name__ == "__main__":
    guesses = {
        "mal": [("r", 1), ("i", 2)],
        "nmal": [("e", 4)],
        "unmatched": "slatpon"
    }
    #guesses = {"mal": [], "nmal": [("p", 4), ("r", 3), ("f", 3)], "unmatched": ""}

    possibilities = get_possibilities(guesses)
    c = Counter([c for word in possibilities for c in word])
    print(possibilities)
    print(json.dumps(sorted(c.items(), key=lambda x: x[1]), indent=2))
