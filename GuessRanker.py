import random

from collections import defaultdict

from Matcher import Matcher
from RankMemoizer import RankMemoizer

LOCATION_MATCH_WEIGHT = 2

class GuessRanker:
    to = '\u001b[1A'

    def __init__(self, solutions, guesses):
        self.solutions = solutions
        self.guesses = guesses
        self.guess_set = set(self.guesses)
        self.matcher = Matcher(guesses)
        self.rank_memoizer = RankMemoizer(self.get_descriptor())

    def rank_guesses(self):
        scores = self.rank_memoizer.maybe_get_memo(self.guesses)
        if scores:
            return scores

        print()
        scores = defaultdict(list)
        for (idx, solution) in enumerate(self.guesses):
            print("%sBuilding ranking (%d/%d)" % (self.to, idx, len(self.guesses)))

            for guess in self.guesses:
                scores[guess].append(self.score_guess(solution, guess))

        sorted_scores = self.sort_scores(scores)
        self.rank_memoizer.memoize(self.guesses, sorted_scores)
        return sorted_scores

    def get_descriptor(self):
        return 'base'

class GuessMatchRanker(GuessRanker):
    @staticmethod
    def factory(solutions, guesses):
        return GuessMatchRanker(solutions, guesses)

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
    def factory(solutions, guesses):
        return GuessWinnowRanker(solutions, guesses)

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
    def factory(solutions, guesses):
        return GuessRandomRanker(solutions, guesses)

    def get_descriptor(self):
        return 'random'

    def score_guess(self, solution, guess):
        return 1

    def sort_scores(self, scores):
        scores = [(item[0], 1) for item in scores.items()]
        random.shuffle(scores)
        return scores
