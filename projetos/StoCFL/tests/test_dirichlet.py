import os
import unittest

import numpy as np
import torch
from fedlab.utils.functional import evaluate
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

from datasets import dirichlet_partition
from functional import evaluate_recall

MNIST_ROOT = "./datasets/mnist/"
N = 240


def mnist_targets():
    return datasets.MNIST(MNIST_ROOT, train=True).targets.numpy()


@unittest.skipUnless(os.path.isdir(os.path.join(MNIST_ROOT, "MNIST", "raw")), "MNIST not downloaded in datasets/mnist/")
class TestDirichletPartition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.targets = mnist_targets()

    def partition(self, alpha, seed):
        return dirichlet_partition(self.targets, N, alpha, seed)

    def test_mesma_seed_mesma_particao(self):
        a, b = self.partition(0.5, 3), self.partition(0.5, 3)
        self.assertEqual(sorted(a), sorted(b))
        for cid in a:
            np.testing.assert_array_equal(a[cid], b[cid])

    def test_seeds_e_alphas_diferentes_mudam_a_particao(self):
        base = self.partition(0.5, 0)
        for other in (self.partition(0.5, 1), self.partition(1.0, 0)):
            self.assertTrue(any(len(base[c]) != len(other[c]) or (base[c] != other[c]).any() for c in base))

    def test_tamanhos_e_cobertura(self):
        for alpha in (0.5, 1.0):
            p = self.partition(alpha, 0)
            self.assertEqual(sorted(p), list(range(N)))
            self.assertGreaterEqual(min(len(v) for v in p.values()), 50)
            todos = np.concatenate(list(p.values()))
            # every sample goes to exactly one client
            self.assertEqual(len(todos), len(self.targets))
            self.assertEqual(len(np.unique(todos)), len(self.targets))

    def test_alpha_menor_da_mais_skew(self):
        def max_share(p):
            return np.mean([np.bincount(self.targets[v], minlength=10).max() / len(v) for v in p.values()])
        self.assertGreater(max_share(self.partition(0.5, 0)), max_share(self.partition(1.0, 0)))

    def test_nao_altera_o_gerador_global(self):
        np.random.seed(123)
        state = np.random.get_state()
        self.partition(1.0, 0)
        after = np.random.get_state()
        self.assertEqual(state[0], after[0])
        np.testing.assert_array_equal(state[1], after[1])
        self.assertEqual(state[2:], after[2:])


class TestEvaluateRecall(unittest.TestCase):
    def test_igual_ao_evaluate_do_fedlab_e_recall_por_classe(self):
        torch.manual_seed(0)
        model = torch.nn.Linear(5, 3)
        x = torch.randn(70, 5)
        y = torch.randint(0, 3, (70,))
        loader = DataLoader(TensorDataset(x, y), batch_size=16)
        crit = torch.nn.CrossEntropyLoss()

        loss, acc = evaluate(model, crit, loader)
        loss_r, acc_r, recall = evaluate_recall(model, crit, loader)
        self.assertEqual(loss, loss_r)
        self.assertEqual(acc, acc_r)

        with torch.no_grad():
            pred = model(x).argmax(1)
        for c in range(3):
            self.assertAlmostEqual(recall[c], ((pred == c) & (y == c)).sum().item() / (y == c).sum().item())

    def test_classe_sem_amostra_da_none(self):
        model = torch.nn.Linear(2, 3)
        loader = DataLoader(TensorDataset(torch.randn(8, 2), torch.zeros(8, dtype=torch.long)), batch_size=8)
        _, _, recall = evaluate_recall(model, torch.nn.CrossEntropyLoss(), loader)
        self.assertIsNotNone(recall[0])
        self.assertIsNone(recall[1])
        self.assertIsNone(recall[2])


if __name__ == "__main__":
    unittest.main()
