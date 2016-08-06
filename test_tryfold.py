import tryfold
import unittest

class TestIntersect(unittest.TestCase):
    def test_bowtie(self):
        y = [0,1,2,3]
        pts = [[0,0],[1,1],[1,0],[0,1]]
        self.assertFalse(tryfold.planar_poly(pts,y))
    def test_prob16(self):
        # y = 
        # pts = [(-0.2, 2.2), (0.0, 0.625), (2.2, 2.2), (0.0, 1.1), (-0.2, -0.2), (0.3, 0.7000000000000001), (1.1, 0.0), (1.1, 0.625), (2.1, 0.0), (0.0, 0.0), (1.0, 1.225), (-0.3, 0.4), (2.1, 0.125), (1.0, 1.1), (1.0, 0.0), (2.2, -0.2), (1.0, 0.125)]
        pass

if __name__ == '__main__':
    unittest.main()
