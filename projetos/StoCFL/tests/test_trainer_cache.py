import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace

import torch

from datasets import BaseDataset
from models.linear import SimpleLinear
from trainer import RotatedMNISTTrainer


class TestRotatedMNISTTrainerCache(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        save_dir = os.path.join(self.dir, "data")
        args = SimpleNamespace(dataset="mnist", root=self.dir, save_dir=save_dir, n=2, lr=0.1)
        self.trainer = RotatedMNISTTrainer(SimpleLinear(), args, cuda=False)
        torch.manual_seed(0)
        for cid in range(2):
            dataset = BaseDataset([torch.rand(1, 28, 28) for _ in range(7)], [int(y) for y in torch.randint(0, 10, (7,))])
            torch.save(dataset, os.path.join(save_dir, "train", "data{}.pkl".format(cid)))
        torch.save(BaseDataset([torch.rand(1, 28, 28) for _ in range(5)], torch.randint(0, 10, (5,))), os.path.join(save_dir, "test", "data0.pkl"))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def assert_same_batches(self, a, b):
        self.assertEqual(len(a), len(b))
        for (xa, ya), (xb, yb) in zip(a, b):
            self.assertTrue(torch.equal(xa, xb))
            self.assertTrue(torch.equal(ya, yb))

    def test_mesmos_lotes_que_o_data_loader(self):
        for batch_size in (None, 3):
            for cid in range(2):
                self.assert_same_batches(self.trainer.get_batches(cid, batch_size), list(self.trainer.dataset.get_data_loader(cid, batch_size)))
        self.assert_same_batches(self.trainer.get_test_dataloader(0), list(self.trainer.dataset.get_data_loader(0, batch_size=4096, type="test")))
        self.assertEqual([len(x) for x, _ in self.trainer.get_batches(0, 3)], [3, 3, 1])

    def test_le_o_disco_uma_vez(self):
        first = self.trainer.get_batches(0, None)
        test = self.trainer.get_test_dataloader(0)
        shutil.rmtree(os.path.join(self.trainer.dataset.dir, "train"))
        shutil.rmtree(os.path.join(self.trainer.dataset.dir, "test"))
        self.assertIs(self.trainer.get_batches(0, None), first)
        self.assertIs(self.trainer.get_test_dataloader(0), test)
        # a client that was never read is not in the cache
        with self.assertRaises(FileNotFoundError):
            self.trainer.get_batches(1, None)

    def test_chaves_separadas_por_lote_e_tipo(self):
        self.trainer.get_batches(0, None)
        self.trainer.get_batches(0, 3)
        self.trainer.get_test_dataloader(0)
        self.assertEqual(set(self.trainer.batches), {(0, None, "train"), (0, 3, "train"), (0, 4096, "test")})


if __name__ == "__main__":
    unittest.main()
