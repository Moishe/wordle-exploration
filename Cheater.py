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

    ranked_guesses = defaultdict(int)
    # See which of the remaining words eliminates the most words
    for word in solutions:
        for possible_word in possible_words:
            if is_possible(word, possible_word):
                ranked_guesses[word] += 1

    print(possible_words, ranked_guesses['pizza'])
    ranked_guesses = sorted(ranked_guesses.items(), key=lambda x: x[1])
    #print(ranked_guesses)



if __name__ == "__main__":
    guesses = [
        {"nmal": [(2, "a")], "mal": [], "unmatched": "slte"},
        {"nmal": [(3, "i")], "mal": [], "unmatched": "chor"},
    ]

    possibilities = get_possibilities(guesses)

    print(possibilities)
