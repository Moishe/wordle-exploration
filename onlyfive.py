import argparse
import codecs
import heapq
import json
from nis import match
import random
import statistics
import sys

from collections import defaultdict

from Corpus import Corpus
import GuessRanker
from RankMemoizer import RankMemoizer
import Solver

SOLUTION_WORDS = 3000
GUESS_WORDS = 12000

SOLUTION_SAMPLE_SIZE = 3000
GUESS_SAMPLE_SIZE = 12000

USE_REAL_DICT = True

LOCATION_MATCH_WEIGHT = 2
MAX_CANDIDATE_GUESSES = 20

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("Requires python 3")
        exit(1)

    args = argparse.ArgumentParser('wordle solver')
    args.add_argument('--solution', type=str, help='If specified, solve for this solution')
    args.add_argument('--discardmemo', type=str, help='If specified, discard memoization of this descriptor')
    args.add_argument('--print_solutions', type=bool, help='Print all the solutions')
    args.add_argument('--save_sample', type=str, help='Save the words used in this model to the given filename')
    p = args.parse_args()

    if p.solution:
        solutions = [p.solution]
    elif USE_REAL_DICT:
        solutions = Corpus.get_real_solutions()
    else:
        solutions = random.choices(Corpus.get_top_n(SOLUTION_WORDS), k=SOLUTION_SAMPLE_SIZE)

    if GUESS_WORDS == GUESS_SAMPLE_SIZE:
        random_guesses = Corpus.get_top_n(GUESS_WORDS)
    else:
        random_guesses = random.choices(Corpus.get_top_n(GUESS_WORDS), k=GUESS_SAMPLE_SIZE)

    guesses = list(set(solutions).union(set(random_guesses)))

    if USE_REAL_DICT:
        guesses = list(set(Corpus.get_real_solutions()).union(set(random_guesses)))

    print("Solution corpus size: %d\nGuess corpus size: %d" % (len(solutions), len(guesses)))

    if p.save_sample:
        f = open(p.save_sample, 'w')
        for guess in guesses:
            f.write(guess + '\n')
        f.close()

    print("Running solvers")
    RankMemoizer.load()
    if p.discardmemo:
        RankMemoizer.discard(p.discardmemo)

    factories = [
        GuessRanker.GuessRandomRanker.factory, 
        GuessRanker.GuessMatchRanker.factory, 
        #GuessRanker.GuessWinnowRanker.factory,
        GuessRanker.GuessFrequencyRanker.factory
    ]
    results = defaultdict(list)
    for (idx, factory) in enumerate(factories):
        solver = Solver.Solver(guesses, factory, p.print_solutions)
        name = factory([]).get_descriptor()
        for solution in solutions:
            steps = solver.solve(solution)
            results[name].append(steps)

    RankMemoizer.save()

    print("Total combos: %d" % len(GuessRanker.seen_possible_words))

    for (name, result) in results.items():
        print("%s results" % name)
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
            if k == 7:
                k = 'X'
            print("%s (%s): %s" % (str(k), str(v).ljust(4), '#' * count))
        print()
