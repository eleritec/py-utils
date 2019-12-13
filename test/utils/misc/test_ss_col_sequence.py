import unittest

from utils.misc.ss_col_sequence import get_sequence, next
from utils.general import ListIndex
indices = ListIndex.list

class TestSSColSequence(unittest.TestCase):

    def test_next_with_empty(self):
        self.assertEqual(next(''), 'A')
        self.assertEqual(next('   '), 'A')
        self.assertEqual(next(None), 'A')

    def test_simple_next(self):
        self.assertEqual(next('a'), 'B')
        self.assertEqual(next('A'), 'B')
        self.assertEqual(next('  \nA \t'), 'B')
        self.assertEqual(next(' a   '), 'B')

    def test_next_multi_letter(self):
        self.assertEqual(next('foo'), 'FOP')
        self.assertEqual(next('bar'), 'BAS')
        self.assertEqual(next('baz'), 'BBA')

    def test_next_garbage(self):
        self.assertEqual(next('a a'), 'A')
        self.assertEqual(next('123'), 'A')
        self.assertEqual(next('foo*&'), 'A')
        self.assertEqual(next('!(&23'), 'A')

    def test_sequence_with_empty_seed(self):
        self.assertList(get_sequence(None, 3), 'A', 'B', 'C')
        self.assertList(get_sequence('', 3), 'A', 'B', 'C')
        self.assertList(get_sequence('    ', 3), 'A', 'B', 'C')
        self.assertList(get_sequence('*&$', 3), 'A', 'B', 'C')

    def test_simple_sequence(self):
        self.assertList(get_sequence('A', 3), 'A', 'B', 'C')
        self.assertList(get_sequence('Y', 4), 'Y', 'Z', 'AA', 'AB')
        self.assertList(get_sequence('foo', 4), 'FOO', 'FOP', 'FOQ', 'FOR')

    def test_complex_formulae_001(self):
        to_formula = lambda col: '${}3-sum({}20:{}100)'.format(col.even_odd('F', 'G'), col.value, col.value)
        formulae = [to_formula(col) for col in indices(get_sequence('J', 10, 2))]

        self.assertEqual(len(formulae), 10)
        self.assertEqual(formulae[0], '$F3-sum(J20:J100)')
        self.assertEqual(formulae[1], '$G3-sum(L20:L100)')
        self.assertEqual(formulae[2], '$F3-sum(N20:N100)')
        self.assertEqual(formulae[3], '$G3-sum(P20:P100)')
        self.assertEqual(formulae[4], '$F3-sum(R20:R100)')
        self.assertEqual(formulae[5], '$G3-sum(T20:T100)')
        self.assertEqual(formulae[6], '$F3-sum(V20:V100)')
        self.assertEqual(formulae[7], '$G3-sum(X20:X100)')
        self.assertEqual(formulae[8], '$F3-sum(Z20:Z100)')
        self.assertEqual(formulae[9], '$G3-sum(AB20:AB100)')

    def assertList(self, actual, *expected):
        self.assertEqual(actual, list(expected))