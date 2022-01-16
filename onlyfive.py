import argparse
import heapq
import json
import random
import sys

from collections import defaultdict

SOLUTION_WORDS = 2000
GUESS_WORDS = 2100

SOLUTION_SAMPLE_SIZE = 2000
EXTRA_GUESS_SAMPLE_SIZE = 0

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

class ProbabilityBuilder:
    def __init__(self, guesses, words_with_letter, words_with_letter_at_location):
        self.guesses = guesses
        self.words_with_letter = words_with_letter
        self.words_with_letter_at_location = words_with_letter_at_location
        self.words_to_force = {}
        self.words_to_ignore = set()

    def force(self, level, words_to_force):
        self.words_to_force[level] = words_to_force

    def get_results(self, solution, guess):
        match_at_loc = []
        match_not_at_loc = []
        for (idx, l) in enumerate(guess):
            if l == solution[idx]:
                match_at_loc.append((idx, l))
            elif l in solution:
                match_not_at_loc.append(l)

        return (match_at_loc, match_not_at_loc)

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
            (match_at_loc, match_not_at_loc) = self.get_results(solution, guess)
            if len(match_at_loc) == 5:
                if len(path) > 0:
                    #print("Found match: %s" % path)
                    if not root:
                        print("uh oh")
                    results[root].append(depth)
                    continue
                else:
                    continue

            new_possibilities = possibilities.copy()
            new_possibilities.remove(guess)
            for mal in match_at_loc:
                new_possibilities.intersection_update(self.words_with_letter_at_location[mal])
            for mnal in match_not_at_loc:
                new_possibilities.intersection_update(self.words_with_letter[mnal])

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
            new_possibilities = possibilities.copy()
            new_possibilities.remove(guess)
            for mal in match_at_loc:
                new_possibilities.intersection_update(self.words_with_letter_at_location[mal])
            for mnal in match_not_at_loc:
                new_possibilities.intersection_update(self.words_with_letter[mnal])
            self.find_all_paths(solution, results, root, depth + 1, new_possibilities, path + [guess])

class Solver:
    def __init__(self, results):
        self.results = results
        self.goal = goal

    def solve(goal):
        pass

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Requires python 3")
        exit(1)

    args = argparse.ArgumentParser('wordle solver')
    args.add_argument('--results', type=str, help='specifier for the results file; will be generated (slowly) if not specified')
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

    prop_builder = ProbabilityBuilder(guesses, words_with_letter, words_with_letter_at_location)
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
    else:
        f = open('results.json')
        results = json.load(f)
        print(results)

