import argparse
import heapq
import json
import random
import sys

from collections import defaultdict

SOLUTION_WORDS = 2000
GUESS_WORDS = 2100

SOLUTION_SAMPLE_SIZE = 500
EXTRA_GUESS_SAMPLE_SIZE = 100

PRUNE_TOP = 10
RESULTS_MAX = 100

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


class ProbabilityBuilder:
    def __init__(self, guesses, matcher):
        self.guesses = guesses
        self.words_to_force = {}
        self.words_to_ignore = set()
        self.matcher = matcher

    def force(self, level, words_to_force):
        self.words_to_force[level] = words_to_force

    def find_all_paths(self, solution, results, root=None, depth=0, possibilities=None, path=[]):
        if (depth == 5):
            results[root].append(32768)
            return

        if possibilities == None:
            possibilities = set(self.guesses)

        #print("%s: %d, %d" % (solution, depth, len(possibilities)))

        paths = []

        forcing = depth in self.words_to_force
        if forcing:
            guesses = set(self.words_to_force[depth]) - self.words_to_ignore
        else:
            guesses = possibilities

        for guess in guesses:
            (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
            if len(match_at_loc) == 5:
                if len(path) > 0:
                    #print("Found match: %s" % path)
                    if not root:
                        print("uh oh")
                    results[root].append(depth)
                    continue
                else:
                    continue

            new_possibilities = self.matcher.get_possible_words(possibilities, guess, match_at_loc, match_not_at_loc, unmatched)

            if len(new_possibilities) == 0:
                print("Something is wrong!", solution, guess, match_not_at_loc, match_at_loc)
                exit(1)
            else:
                if forcing:
                    if depth == 0:
                        root = guess
                    self.find_all_paths(solution, results, root, depth + 1, new_possibilities, path + [guess])
                else:
                    weight = len(new_possibilities)
                    heapq.heappush(paths, (weight, guess, match_at_loc, match_not_at_loc))

        if forcing:
            return

        for i in range(0, min(PRUNE_TOP, len(paths))):
            (l, guess, match_at_loc, match_not_at_loc) = heapq.heappop(paths)
            if depth == 0:
                root = guess
            new_possibilities = self.matcher.get_possible_words(possibilities, guess, match_at_loc, match_not_at_loc)
            self.find_all_paths(solution, results, root, depth + 1, new_possibilities, path + [guess])

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
        for solution in self.solutions:
            for guess in self.guesses:
                (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(solution, guess)
                score = len(match_at_loc) * 2 + len(match_not_at_loc)
                scores[guess].append(score)
                new_possibilities = self.matcher.get_possible_words(guess_set, guess, match_at_loc, match_not_at_loc, unmatched)
                winnow_scores[guess].append(len(new_possibilities))                

        scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in scores.items()]
        scores = list(reversed(sorted(scores, key=lambda item:item[1])))

        winnow_scores = [(item[0], float(sum(item[1]))/float(len(item[1]))) for item in winnow_scores.items()]
        winnow_scores = sorted(winnow_scores, key=lambda item:item[1])
        return (scores, winnow_scores)

class Solver:
    def __init__(self, results, guesses):
        self.results = results
        self.guesses = guesses

    def solve(self, goal, start_word=None, depth=0, match_at_loc=None, match_not_at_loc=None):
        if not start_word:
            if self.results:
                start_word = self.results[0][0]
            else:
                start_word = random.choices(guesses)
        
        (match_at_loc, match_not_at_loc, unmatched) = Matcher.get_results(goal, start_word)
        print(goal, start_word, match_at_loc, match_not_at_loc)
        new_possibilities = matcher.get_possible_words(set(self.guesses), start_word, match_at_loc, match_not_at_loc, unmatched)
        print(new_possibilities)

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
        exit(1)

    def solve(self):
        print("looking for %s" % self.solution)
        states = []
        for i in range(0,5):
            candidate = self.get_candidate()
            print("trying %s" % candidate)
            states.append(candidate)
            if candidate == self.solution:
                print("Found: %s" % states)
                return i
            (match_at_loc, match_not_at_loc, unmatched) = self.matcher.get_results(self.solution, candidate)
            self.guesses = matcher.get_possible_words(set(self.guesses), candidate, match_at_loc, match_not_at_loc, unmatched)

            if self.solution not in self.guesses:
                print("This is weird, solution %s not in guesses")

        print("Unable to find: %s" % states)
        return 5


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Requires python 3")
        exit(1)

    args = argparse.ArgumentParser('wordle solver')
    args.add_argument('--results', type=str, help='specifier for the results file; will be generated (slowly) if not specified')
    args.add_argument('--density_file', type=str, help='file containing density scores')
    p = args.parse_args()

    solutions = random.choices(get_top_n(SOLUTION_WORDS), k=SOLUTION_SAMPLE_SIZE)

    random_guesses = random.choices(get_top_n(GUESS_WORDS), k=EXTRA_GUESS_SAMPLE_SIZE)
    guesses = solutions + random_guesses

    words_with_letter = defaultdict(set)
    words_with_letter_at_location = defaultdict(set)
    for word in guesses:
        for (idx, letter) in enumerate(word):
            words_with_letter[letter].add(word)
            words_with_letter_at_location[(idx, letter)].add(word)

    matcher = Matcher(words_with_letter, words_with_letter_at_location)

    density_finder = InformationDensityFinder(solutions, guesses, matcher)
    if p.density_file:
        density_finder.load(p.density_file)
    else:
        scores = density_finder.find_high_density_guesses()
        density_finder.save(scores[0], scores[1])

    results = {0: defaultdict(int), 1: defaultdict(int)}
    for goal in solutions:
        match_density_solver = DensitySolver(goal, guesses, scores[0], matcher)
        results[0][match_density_solver.solve()] += 1

        winnow_density_solver = DensitySolver(goal, guesses, scores[1], matcher)
        results[1][winnow_density_solver.solve()] += 1

    for i in range(0, 2):
        print(['match', 'winnow'][i])
        for j in range(0, 6):
            if j <= 4:
                descriptor = str(j + 1) + '   '
            else:
                descriptor = 'fail'
            print("%s %s" % (descriptor, '#' * results[i][j]))
    exit(0)

    prop_builder = ProbabilityBuilder(guesses, matcher)
    if not p.results:
        results = defaultdict(list)
        for solution in solutions:
            print("Looking for %s" % solution)
            prop_builder.find_all_paths(solution, results)

        print("We have %d candidates, re-running the simulation" % len(results.keys()))

        # okay now we have a list of candidate results. Now go through the n of them that led to the most results
        frequent_results = list(reversed(sorted([(k, len(v)) for (k,v) in results.items()], key=lambda item: item[1])))
        prop_builder.force(0, [v[0] for v in frequent_results[:RESULTS_MAX]])
        results = defaultdict(list)

        for solution in solutions:
            print("Reconciling %s" % solution)
            prop_builder.find_all_paths(solution, results)

        f = open('results.json', 'w')
        average_results = sorted([(k, float(sum(v))/float(len(v))) for (k,v) in results.items()], key=lambda item: item[1])
        f.write(json.dumps(list(average_results)) + '\n')
        f.flush()

        results = average_results
    else:
        f = open(p.results)
        results = json.load(f)
        print(results)

    words = ['panic', 'disco', 'query', 'scram', 'mouse', 'house', 'prion', 'poker']
    solver = Solver(results, guesses)
    for word in words:
        solver.solve(word)
