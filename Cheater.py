import Corpus
import Matcher
from collections import defaultdict

def is_possible(word, possible_word):
    for (idx, letter) in enumerate(word):
        if letter == possible_word[idx]:
            return True
    return False

def get_possibilities(guesses):
    solutions = Corpus.Corpus.get_real_solutions()
    if 'panda' in solutions:
        print("panda is in solutions")
    else:
        print("panda is not in solutions")
    matcher = Matcher.Matcher(solutions)

    possible_words = set(Corpus.Corpus.get_real_solutions())
    aggregate_guess = {
        "mal": set(),
        "nmal": set(),
        "unmatched": set(),
    }
    for guess in guesses:
        aggregate_guess = {
            "mal": aggregate_guess["mal"].union(set(guess["mal"])),
            "nmal": aggregate_guess["nmal"].union(set(guess["nmal"])),
            "unmatched": aggregate_guess["unmatched"].union(set(guess["unmatched"])),
        }

    print(aggregate_guess)

    possible_words = matcher.get_possible_words(
        possible_words,
        None,
        set(aggregate_guess["mal"]),
        set(aggregate_guess["nmal"]),
        aggregate_guess["unmatched"],
    )
    print(possible_words)

    possibilities = defaultdict(set)
    full_eliminations = defaultdict(set)
    for possible_word in possible_words:
        impossible_words = set(possible_words)
        for guess in ['panda']: #possible_words:
            result = matcher.get_results(possible_word, guess)
            mal = set(result[0]).union(aggregate_guess["mal"])
            nmal = set(result[1]).union(aggregate_guess["nmal"])
            unmatched = result[2].union(aggregate_guess["unmatched"])
            results = matcher.get_possible_words(
                possible_words,
                guess,
                mal,
                nmal,
                unmatched,
            )
            print(possible_word, guess, mal, nmal, unmatched, results)
            if len(results) == 1:
                full_eliminations[guess].add(possible_word)

    print(full_eliminations)
    """
    possibilities = list(filter(lambda x: len(x[1]) > 0, possibilities.items()))
    possibilities = sorted(possibilities, key=lambda x: len(x[1]))
    print(possibilities[:10])
    """

if __name__ == "__main__":
    guesses = [
        {"nmal": [(2, "a")], "mal": [], "unmatched": "slte"},
        {"nmal": [(3, "i")], "mal": [], "unmatched": "chor"},
    ]

    possibilities = get_possibilities(guesses)
