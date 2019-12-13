import unittest

from utils.misc.ss_col_sequence import get_sequence, next

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

    def assertList(self, actual, *expected):
        self.assertEqual(actual, list(expected))