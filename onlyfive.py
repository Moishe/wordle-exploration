import argparse
import codecs
import heapq
import json
from nis import match
import random
import statistics
import sys

from collections import defaultdict

import GuessRanker
from RankMemoizer import RankMemoizer
import Solver
from Corpus import Corpus
from Matcher import Matcher

SOLUTION_WORDS = 3000
GUESS_WORDS = 3000

SOLUTION_SAMPLE_SIZE = 3000
GUESS_SAMPLE_SIZE = 0

USE_REAL_DICT = True

LOCATION_MATCH_WEIGHT = 2
MAX_CANDIDATE_GUESSES = 20

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Requires python 3")
        exit(1)

    args = argparse.ArgumentParser('wordle solver')
    args.add_argument('--density_file', type=str, help='file containing density scores')
    p = args.parse_args()

    if USE_REAL_DICT:
        solutions = Corpus.get_real_solutions()
    else:
        solutions = random.choices(Corpus.get_top_n(SOLUTION_WORDS), k=SOLUTION_SAMPLE_SIZE)

    if GUESS_WORDS == GUESS_SAMPLE_SIZE:
        random_guesses = Corpus.get_top_n(GUESS_WORDS)
    else:
        random_guesses = random.choices(Corpus.get_top_n(GUESS_WORDS), k=GUESS_SAMPLE_SIZE)
    guesses = list(set(solutions).union(set(random_guesses)))

    print("Solution corpus size: %d\nGuess corpus size: %d" % (len(solutions), len(guesses)))

    print("Running solvers")
    RankMemoizer.load()
    factories = [GuessRanker.GuessRandomRanker.factory, GuessRanker.GuessMatchRanker.factory, GuessRanker.GuessWinnowRanker.factory]
    results = defaultdict(list)
    for (idx, factory) in enumerate(factories):
        solver = Solver.Solver(guesses, factory, True)
        for solution in solutions:
            steps = solver.solve(solution)
            results[idx].append(steps)

    RankMemoizer.save()

    for (idx, result) in results.items():
        print("  mean:   %f" % statistics.mean(result))
        print("  median: %d" % statistics.median(result))
        print("  mode:   %d" % statistics.mode(result))

        # build a histogram
        histogram = defaultdict(int)
        for j in result:
            histogram[j] += 1
        m = max([item[1] for item in histogram.items()])
        for k,v in sorted(histogram.items(), key=lambda item: item[0]):
            count = int(float(v)/float(m) * 80)
            print("%d (%s): %s" % (k, str(v).ljust(4), '#' * count))
        print()
