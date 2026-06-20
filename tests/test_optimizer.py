import unittest

from nemo.optimizers import nelder_mead


class OptimizerTests(unittest.TestCase):
    def test_nelder_mead_minimizes_simple_quadratic(self):
        def objective(values):
            x, y = values
            return (x - 0.25) ** 2 + (y - 0.75) ** 2

        best, value, evaluations, iterations = nelder_mead(
            objective,
            [0.8, 0.2],
            max_iter=120,
            tolerance=1e-8,
        )

        self.assertLess(value, 1e-4)
        self.assertAlmostEqual(best[0], 0.25, places=2)
        self.assertAlmostEqual(best[1], 0.75, places=2)
        self.assertGreater(evaluations, 0)
        self.assertGreater(iterations, 0)


if __name__ == "__main__":
    unittest.main()
