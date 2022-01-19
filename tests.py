import unittest
import GuessRanker

from Corpus import Corpus
from Matcher import Matcher

DEFAULT_GUESSES = ['wooer', 'about', 'other', 'which', 'their', 'there', 'first', 'would', 'these', 'click']

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
                
class MatcherTests(unittest.TestCase):

  def setUp(self):
    self.guesses = Corpus.get_top_n(100)

  def test_getresults(self):
    matcher = Matcher(DEFAULT_GUESSES)
    (match_at_loc, match_not_at_loc, unmatched_letters) = matcher.get_results('wooer', 'click')
    self.assertEqual(match_at_loc, [])
    self.assertEqual(match_not_at_loc, [])
    self.assertEqual(unmatched_letters, set([l for l in 'click']))

    (match_at_loc, match_not_at_loc, unmatched_letters) = matcher.get_results('wooer', 'efete')
    self.assertEqual(match_not_at_loc, [(0, 'e')])

  def test_match_guess_ranker(self):
    match_guess_ranker = GuessRanker.GuessMatchRanker(self.guesses, self.guesses)
    scores = match_guess_ranker.rank_guesses()
    self.assertEqual(scores[0][0], 'store')

  def test_winnow_guess_ranker(self):
    winnow_guess_ranker = GuessRanker.GuessWinnowRanker(self.guesses, self.guesses)
    scores = winnow_guess_ranker.rank_guesses()
    self.assertEqual(scores[0][0], 'store')

if __name__ == '__main__':
    unittest.main()    