from collections import defaultdict

GREEN = '\u001b[32m'
YELLOW = '\u001b[33m'
RESET = '\u001b[0m'
BLOCK = '\u2589'

class Matcher:
    def __init__(self, guesses):
        self.words_with_letter = defaultdict(set)
        self.words_with_letter_at_location = defaultdict(set)

        for word in guesses:
            for (idx, letter) in enumerate(word):
                self.words_with_letter[letter].add(word)
                self.words_with_letter_at_location[(idx, letter)].add(word)

    @staticmethod
    def get_results(solution, guess):
        match_at_loc = []
        match_not_at_loc = []
        unmatched_letters = set()
        new_solution = ''
        new_guess = ''
        matched_letters = set()
        for (idx, l) in enumerate(guess):
            if l == solution[idx]:
                match_at_loc.append((idx, l))
                new_solution += '_'
                new_guess += '_'
                matched_letters.add(l)
            else:
                new_solution += solution[idx]
                new_guess += l

        for (idx, l) in enumerate(new_guess):
            if l == '_':
                continue
            if l in new_solution:
                match_not_at_loc.append((idx, l))
                new_solution = new_solution.replace(l, '_', 1)
                matched_letters.add(l)
            elif l not in matched_letters:
                unmatched_letters.add(l)

        return (match_at_loc, match_not_at_loc, unmatched_letters)

    def get_possible_words(self, possibilities, guess, match_at_loc, match_not_at_loc, unmatched):
        new_possibilities = possibilities.copy()
        for mal in match_at_loc:
            new_possibilities.intersection_update(self.words_with_letter_at_location[mal])
        for mnal in match_not_at_loc:
            new_possibilities.intersection_update(self.words_with_letter[mnal[1]])
        for mnal in match_not_at_loc:
            new_possibilities.difference_update(self.words_with_letter_at_location[mnal])
        for u in unmatched:
            new_possibilities.difference_update(self.words_with_letter[u])

        # it's possible that the guess was not excluded from the list of possible words,
        # in the case of multiple letter being guessed but not matched, eg. if the
        # guess is "abase" and the solution is "abuse"
        new_possibilities.discard(guess)

        return new_possibilities

    @staticmethod
    def escaped_word(word, match_at_loc, match_not_at_loc):
        word_with_highlights = ''
        for (idx, l) in enumerate(word):
            if (idx, l) in match_at_loc:
                word_with_highlights += GREEN + l + RESET
            elif (idx, l) in match_not_at_loc:
                word_with_highlights += YELLOW + l + RESET
            else:
                word_with_highlights += l
        return word_with_highlights

    @staticmethod
    def obfuscated_escaped_word(word, match_at_loc, match_not_at_loc):
        word_with_highlights = ''
        for (idx, l) in enumerate(word):
            if (idx, l) in match_at_loc:
                word_with_highlights += GREEN + BLOCK + RESET
            elif (idx, l) in match_not_at_loc:
                word_with_highlights += YELLOW + BLOCK + RESET
            else:
                word_with_highlights += BLOCK
        return word_with_highlights
