import random
import unittest

from availability import Availability


def trace(n, drop, rounds, seed, num_rounds):
    availability = Availability(n, drop, rounds, seed)
    return [availability.step() for _ in range(num_rounds)]


def absences(rows, c):
    """Lengths of the complete absences of client c (a run cut by the end of the trace is dropped)."""
    lengths, run = [], 0
    for row in rows:
        if not row[c]:
            run += 1
        elif run:
            lengths.append(run)
            run = 0
    return lengths


def longest_run(rows, c):
    longest = run = 0
    for row in rows:
        run = 0 if row[c] else run + 1
        longest = max(longest, run)
    return longest


class TestAvailability(unittest.TestCase):
    def test_t1_drop_zero_todos_disponiveis_sem_tocar_no_gerador(self):
        availability = Availability(50, 0.0, 10, seed=0)
        state = availability.rng.getstate()
        for _ in range(20):
            up = availability.step()
            self.assertEqual(len(up), 50)
            self.assertTrue(all(up))
        self.assertEqual(availability.rng.getstate(), state)

    def test_t2_mesma_seed_mesmo_traco_e_seeds_diferentes_tracos_diferentes(self):
        a = trace(30, 0.2, 5, seed=7, num_rounds=100)
        self.assertEqual(a, trace(30, 0.2, 5, seed=7, num_rounds=100))
        self.assertNotEqual(a, trace(30, 0.2, 5, seed=8, num_rounds=100))

    def test_t2_nao_consome_o_gerador_global(self):
        random.seed(123)
        state = random.getstate()
        trace(30, 0.2, 5, seed=7, num_rounds=100)
        self.assertEqual(random.getstate(), state)

    def test_t3_ausencia_limitada_a_L_max_e_duracoes_cobrem_1_a_L_max(self):
        n, rounds = 100, 5
        rows = trace(n, 0.1, rounds, seed=0, num_rounds=500)
        durations = set()
        for c in range(n):
            self.assertLessEqual(longest_run(rows, c), rounds)
            durations.update(absences(rows, c))
        self.assertEqual(durations, set(range(1, rounds + 1)))

    def test_t3_ha_rodada_disponivel_entre_duas_ausencias(self):
        # com drop = 0.99, sem a rodada de retorno as ausências se emendariam e passariam de L_max
        n, rounds = 100, 3
        rows = trace(n, 0.99, rounds, seed=0, num_rounds=300)
        for c in range(n):
            self.assertLessEqual(longest_run(rows, c), rounds)
            self.assertTrue(any(row[c] for row in rows))

    def test_t4_disponibilidade_media_bate_com_a_formula(self):
        n, num_rounds = 200, 2000
        for drop, rounds in ((0.1, 10), (0.2, 10)):
            rows = trace(n, drop, rounds, seed=0, num_rounds=num_rounds)
            mean = sum(map(sum, rows)) / (n * num_rounds)
            expected = 1 / (1 + drop * (rounds + 1) / 2)
            self.assertAlmostEqual(mean, expected, delta=0.01)

    def test_t5_valores_invalidos_levantam_value_error(self):
        for drop, rounds in ((-0.1, 1), (1.0, 1), (1.5, 1), (0.1, 0), (0.1, -3)):
            with self.assertRaises(ValueError):
                Availability(10, drop, rounds, seed=0)


if __name__ == "__main__":
    unittest.main()
