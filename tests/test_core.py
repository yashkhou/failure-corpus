import unittest,sys; sys.path.insert(0,'src')
from failure_corpus.core import *
class T(unittest.TestCase):
 def test_pytest(self): self.assertEqual(parse('FAILED a::b - AssertionError: nope')[0].framework,'pytest')
 def test_normalize(self): self.assertIn('<path>',normalize('/tmp/a.py:42 ERROR'))
 def test_dedupe(self): self.assertEqual(dedupe(parse('FAILED a::b - AssertionError: nope\nFAILED a::b - AssertionError: nope'))[0].count,2)
