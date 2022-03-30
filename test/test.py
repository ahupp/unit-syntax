import unit_literals.autohook
import unittest

class Test(unittest.TestCase):
    def test_transforms(self):
        a = 5 km
        b = a meters
        self.assertEqual(b.magnitude, 5001)
        self.assertEqual(b.units, 'meters')

unittest.main()
