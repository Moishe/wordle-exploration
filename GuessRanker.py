import json

from collections import defaultdict

from Matcher import Matcher

LOCATION_MATCH_WEIGHT = 2

class GuessRanker:
    to = '\u001b[1A'

    def __init__(self, solutions, guesses):
        self.solutions = solutions
        self.guesses = guesses
        self.guess_set = set(self.guesses)
        self.matcher = Matcher(guesses)

    def load(self, filename):
        f = open(filename)
        data = json.load(f)
        f.close()
        return data

    def save(self, scores):
        f = open('guess-ranks-%s.json' % self.get_file_suffix(), 'w')
        json.dump([scores], f)
        f.close()

    def rank_guesses(self):
        print()
        scores = defaultdict(list)
        for (idx, solution) in enumerate(self.guesses):
            print("%sBuilding ranking (%d/%d)" % (self.to, idx, len(self.guesses)))

            for guess in self.guesses:
                scores[guess].append(self.score_guess(solution, guess))

        return self.sort_scores(scores)

class GuessMatchRanker(GuessRanker):
    def get_file_suffix():
        return 'match'

    def score_guess(self, solution, guess):
        (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
        return len(match_at_loc) * LOCATION_MATCH_WEIGHT + len(match_not_at_loc)

    def sort_scores(self, scores):
        scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in scores.items()]
        return list(reversed(sorted(scores, key=lambda item:item[1])))


class GuessWinnowRanker(GuessRanker):
    def get_file_suffix():
        return 'winnow'

    def score_guess(self, solution, guess):
        (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
        new_possibilities = self.matcher.get_possible_words(self.guess_set, guess, match_at_loc, match_not_at_loc, unmatched)
        return len(new_possibilities)

    def sort_scores(self, scores):
        winnow_scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in scores.items()]
        return sorted(winnow_scores, key=lambda item:item[1])
