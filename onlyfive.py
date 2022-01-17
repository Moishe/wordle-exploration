import argparse
import codecs
import heapq
import json
import random
import statistics
import sys

from collections import defaultdict

SOLUTION_WORDS = 3000
GUESS_WORDS = 3000

SOLUTION_SAMPLE_SIZE = 3000
GUESS_SAMPLE_SIZE = 5000

USE_REAL_DICT = True

LOCATION_MATCH_WEIGHT = 1
MAX_CANDIDATE_GUESSES = 10

def get_top_n(n):
    # this list is already sorted, so we can optimize a bit!
    f = open('dictionary/norvig-corpus.txt')

    five_freq = []

    for l in f:
        (word, freq) = l.rstrip().split('\t')
        if len(word) == 5:
            five_freq.append(word)
            if len(five_freq) == n:
                return five_freq

def get_real_solutions():
    words = []

    f = open('dictionary/canonical_list.txt')
    for l in f:
        words.append(codecs.decode(l.rstrip(), 'rot_13'))

    return words

class Matcher:
    def __init__(self, words_with_letter, words_with_letter_at_location):
        self.words_with_letter = words_with_letter
        self.words_with_letter_at_location = words_with_letter_at_location

    @staticmethod
    def get_results(solution, guess):
        match_at_loc = []
        match_not_at_loc = []
        seen_letters = set()
        unmatched_letters = set()
        for (idx, l) in enumerate(guess):
            if l == solution[idx]:
                match_at_loc.append((idx, l))
            elif l in solution:
                if l not in seen_letters:
                    match_not_at_loc.append(l)
            else:
                unmatched_letters.add(l)
            seen_letters.add(l)

        return (match_at_loc, match_not_at_loc, unmatched_letters)

    def get_possible_words(self, possibilities, guess, match_at_loc, match_not_at_loc, unmatched):
        new_possibilities = possibilities.copy()
        new_possibilities.discard(guess)
        for mal in match_at_loc:
            new_possibilities.intersection_update(self.words_with_letter_at_location[mal])
        for mnal in match_not_at_loc:
            new_possibilities.intersection_update(self.words_with_letter[mnal])
        for u in unmatched:
            new_possibilities.difference_update(self.words_with_letter[u])

        return new_possibilities

class InformationDensityFinder:
    def __init__(self, solutions, guesses, matcher):
        self.solutions = solutions
        self.guesses = guesses
        self.words_to_force = {}
        self.words_to_ignore = set()
        self.matcher = matcher

    def load(self, filename):
        f = open(filename)
        data = json.load(f)
        f.close()
        return (data[0], data[1])

    def save(self, scores, winnow_scores):
        f = open('densities.json', 'w')
        json.dump([scores, winnow_scores], f)
        f.close()

    def find_high_density_guesses(self):
        scores = defaultdict(list)
        winnow_scores = defaultdict(list)
        guess_set = set(self.guesses)
        for (idx, solution) in enumerate(self.solutions):
            to = '\u001b[1A'
            print("%sBuilding ranking (%d/%d)" % (to, idx, len(self.solutions)))
            for guess in self.guesses:
                (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
                score = len(match_at_loc) * LOCATION_MATCH_WEIGHT + len(match_not_at_loc)
                scores[guess].append(score)
                new_possibilities = self.matcher.get_possible_words(guess_set, guess, match_at_loc, match_not_at_loc, unmatched)
                winnow_scores[guess].append(len(new_possibilities))

        scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in scores.items()]
        scores = list(reversed(sorted(scores, key=lambda item:item[1])))

        winnow_scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in winnow_scores.items()]
        winnow_scores = sorted(winnow_scores, key=lambda item:item[1])
        return (scores, winnow_scores)

class DensitySolver():
    def __init__(self, solution, guesses, densities, matcher):
        self.solution = solution
        self.guesses = set(guesses)
        self.densities = densities
        self.matcher = matcher

    def get_candidate(self):
        for idx in range(0, len(self.densities)):
            if self.densities[idx][0] in self.guesses:
                return self.densities[idx][0]

        print("womp womp, nothing matches :shrug:")
        return None

    def solve(self):
        if not USE_REAL_DICT:
            print("looking for %s" % self.solution)
        states = []
        for i in range(0,5):
            candidate = self.get_candidate()
            if not candidate:
                print("Couldn't find candidate")
                break

            if not USE_REAL_DICT:
                print("trying %s" % candidate)
            states.append(candidate)
            if candidate == self.solution:
                if not USE_REAL_DICT:
                    print("Found: %s" % states)
                return i + 1
            (match_at_loc, match_not_at_loc, unmatched) = self.matcher.get_results(self.solution, candidate)
            self.guesses = self.matcher.get_possible_words(set(self.guesses), candidate, match_at_loc, match_not_at_loc, unmatched)

            if self.solution not in self.guesses:
                print("This is weird, solution %s not in guesses")

        return 6

class RandomSolver(DensitySolver):
    def get_candidate(self):
        return random.choice(list(self.guesses))

class SmartSolver(DensitySolver):
    def get_candidate(self):
        candidates = []
        idx = 0
        guess_set = set(self.guesses)
        while True:
            if self.densities[idx][0] in self.guesses:
                candidate = self.densities[idx][0]
                (match_at_loc, match_not_at_loc, unmatched) = self.matcher.get_results(self.solution, candidate)
                possible_words = self.matcher.get_possible_words(guess_set, candidate, match_at_loc, match_not_at_loc, unmatched)
                heapq.heappush(candidates, (len(possible_words), candidate))

            idx += 1
            if (idx >= len(self.densities)) or len(candidates) >= MAX_CANDIDATE_GUESSES:
                break

        return heapq.heappop(candidates)[1]

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Requires python 3")
        exit(1)

    args = argparse.ArgumentParser('wordle solver')
    args.add_argument('--results', type=str, help='specifier for the results file; will be generated (slowly) if not specified')
    args.add_argument('--density_file', type=str, help='file containing density scores')
    p = args.parse_args()

    if USE_REAL_DICT:
        solutions = get_real_solutions()
    else:
        solutions = random.choices(get_top_n(SOLUTION_WORDS), k=SOLUTION_SAMPLE_SIZE)

    random_guesses = random.choices(get_top_n(GUESS_WORDS), k=GUESS_SAMPLE_SIZE)
    guesses = list(set(solutions).union(set(random_guesses)))

    print("Solution corpus size: %d\nGuess corpus size: %d" % (len(solutions), len(guesses)))

    words_with_letter = defaultdict(set)
    words_with_letter_at_location = defaultdict(set)
    for word in guesses:
        for (idx, letter) in enumerate(word):
            words_with_letter[letter].add(word)
            words_with_letter_at_location[(idx, letter)].add(word)

    matcher = Matcher(words_with_letter, words_with_letter_at_location)

    density_finder = InformationDensityFinder(solutions, guesses, matcher)
    if p.density_file:
        scores = density_finder.load(p.density_file)
        solutions = [item[0] for item in scores[0]]
        print(len(solutions))
    else:
        print("Building guess ranking")
        scores = density_finder.find_high_density_guesses()
        density_finder.save(scores[0], scores[1])

    print("Running solver")
    if USE_REAL_DICT:
        real_solutions = get_real_solutions()
        solutions = list(set(real_solutions).intersection(solutions))

    print("Scanning %d solutions" % len(solutions))

    results = defaultdict(list)
    for goal in solutions:
        match_density_solver = DensitySolver(goal, guesses, scores[0], matcher)
        results[0].append(match_density_solver.solve())

        winnow_density_solver = DensitySolver(goal, guesses, scores[1], matcher)
        results[1].append(winnow_density_solver.solve())

        random_solver = RandomSolver(goal, guesses, None, matcher)
        results[2].append(random_solver.solve())

        smart_solver = SmartSolver(goal, guesses, scores[1], matcher)
        results[3].append(smart_solver.solve())

    for i in range(0, 4):
        print(['match', 'winnow', 'random', 'smart'][i])
        print("  mean:   %f" % statistics.mean(results[i]))
        print("  median: %d" % statistics.median(results[i]))
        print("  mode:   %d" % statistics.mode(results[i]))

        # build a histogram
        histogram = defaultdict(int)
        for j in results[i]:
            histogram[j] += 1
        m = max([item[1] for item in histogram.items()])
        for k,v in sorted(histogram.items(), key=lambda item: item[0]):
            count = int(float(v)/float(m) * 80)
            print("%d (%s): %s" % (k, str(v).ljust(4), '#' * count))
