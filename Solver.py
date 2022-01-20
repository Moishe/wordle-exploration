import random

from Matcher import Matcher

HIGHLIGHT = '\u001b[37m'
RED = '\u001b[31m'
RESET = '\u001b[0m'
GREEN = '\u001b[32m'

class Solver:
    def __init__(self, guesses, ranker_factory, show_status=False):
        self.guesses = guesses
        self.ranker_factory = ranker_factory
        self.show_status = show_status

    def print_solution(self, states, solution):
        return
        if not self.show_status:
            return

        states.append(GREEN + '\u2589' * 5 + RESET)
        print("\n" + ' ' * 10 + "%d/5" % len(states))
        print('\n'.join([' ' * 10 + state for state in states]))

    def get_candidate(self, current_guesses):
        ranker = self.ranker_factory(current_guesses, current_guesses)
        return ranker.get_best_guess()

    def solve(self, solution):
        states = []
        unobfuscated_states = []
        current_guesses = self.guesses.copy()
        for i in range(0,5):
            candidate = self.get_candidate(current_guesses)
            if not candidate:
                print("Couldn't find candidate")
                break

            if candidate == solution:
                self.print_solution(states, solution)
                return i + 1

            matcher = Matcher(current_guesses)
            (match_at_loc, match_not_at_loc, unmatched) = matcher.get_results(solution, candidate)
            states.append(Matcher.obfuscated_escaped_word(candidate, match_at_loc, match_not_at_loc))
            current_guesses = matcher.get_possible_words(set(current_guesses), candidate, match_at_loc, match_not_at_loc, unmatched)
            unobfuscated_states.append("%s (%d)" % (candidate, len(current_guesses)))

            if solution not in current_guesses:
                print("This is weird, solution %s not in guesses (%s) (%s)" % (solution, current_guesses))
                break

        #print('\n          X/5')
        #print('\n'.join([' ' * 10 + state for state in states]))
        print(solution, ','.join(unobfuscated_states))
        return 6

