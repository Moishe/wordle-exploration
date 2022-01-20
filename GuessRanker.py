from hashlib import new
import random

from collections import defaultdict

from Matcher import Matcher
from RankMemoizer import RankMemoizer

LOCATION_MATCH_WEIGHT = 2

class GuessRanker:
    to = '\u001b[1A'

    def __init__(self, guesses):
        self.guesses = guesses
        self.guess_set = set(self.guesses)
        self.matcher = Matcher(guesses)
        self.rank_memoizer = RankMemoizer(self.get_descriptor())
    
    def get_best_guess(self):
        best_guess = self.rank_memoizer.maybe_get_memo(self.guesses)
        if best_guess:
            return best_guess

        print()
        scores = defaultdict(list)
        for (idx, solution) in enumerate(self.guesses):
            print("%sBuilding ranking (%d/%d)" % (self.to, idx + 1, len(self.guesses)))

            for guess in self.guesses:
                scores[guess].append(self.score_guess(solution, guess))

        sorted_scores = self.sort_scores(scores)
        best_guess = sorted_scores[0][0]
        self.rank_memoizer.memoize(self.guesses, best_guess)
        return best_guess

    def get_descriptor(self):
        return 'base'

class GuessMatchRanker(GuessRanker):
    @staticmethod
    def factory(guesses):
        return GuessMatchRanker(guesses)

    def get_descriptor(self):
        return 'match'

    def score_guess(self, solution, guess):
        (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
        return len(match_at_loc) * LOCATION_MATCH_WEIGHT + len(match_not_at_loc)

    def sort_scores(self, scores):
        scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in scores.items()]
        return list(reversed(sorted(scores, key=lambda item:item[1])))


class GuessWinnowRanker(GuessRanker):
    @staticmethod
    def factory(guesses):
        return GuessWinnowRanker(guesses)

    def get_descriptor(self):
        return 'winnow'

    def score_guess(self, solution, guess):
        (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
        new_possibilities = self.matcher.get_possible_words(self.guess_set, guess, match_at_loc, match_not_at_loc, unmatched)
        return len(new_possibilities)

    def sort_scores(self, scores):
        winnow_scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in scores.items()]
        return sorted(winnow_scores, key=lambda item:item[1])

class GuessRandomRanker(GuessRanker):
    @staticmethod
    def factory(guesses):
        return GuessRandomRanker(guesses)

    def get_descriptor(self):
        return 'random'

    def get_best_guess(self):
        return random.choice(list(self.guesses))

class GuessFrequencyRanker(GuessRanker):
    def __init__(self, guesses):
        super().__init__(guesses)

        # build the frequency table
        self.freqs = defaultdict(int)
        self.freqlocs = defaultdict(int)
        for guess in guesses:
            for (idx, l) in enumerate(guess):
                self.freqs[l] += 1
                self.freqlocs[(idx, l)] += 1

    @staticmethod
    def factory(guesses):
        return GuessFrequencyRanker(guesses)

    def get_descriptor(self):
        return 'freqs'

    def get_best_guess(self):
        best_guess = self.rank_memoizer.maybe_get_memo(self.guesses)
        if best_guess:
            return best_guess

        scores = defaultdict(int)
        for (idx, guess) in enumerate(self.guesses):
            for (idx, l) in enumerate(guess):
                if (idx, l) in self.freqlocs:
                    scores[guess] += 2 * self.freqlocs[(idx, l)]
                elif l in self.freqs:
                    scores[guess] += self.freqs[l]

        sorted_scores = list(reversed(sorted(scores.items(), key=lambda item: item[1])))
        best_guess = sorted_scores[0][0]
        self.rank_memoizer.memoize(self.guesses, best_guess)
        return best_guess
