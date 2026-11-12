"""Experimental: StoCFL-FCC+CFL.py plus a split of chained clusters by the CFL of Sattler et al.

Hypothesis and design in docs/hipotese-stocfl-divisao-cfl.md (D-057, D-058). The server, the trainers and the data
come from StoCFL-FCC+CFL.py, which is not changed. After the bi-level training of each round, this script:
  - takes every cluster with 2+ members whose Psi have some pair with cos <= tau (clients that would not merge alone);
  - applies the CFL criterion to the members' updates of the cluster model: ||mean dW|| < eps1 and max ||dW_i|| > eps2;
  - splits it by Algorithm 1 of the CFL paper on the cosine of the dW, if gamma_max < sqrt((1 - alpha_cross_max) / 2);
    both sides keep a copy of the parent cluster model;
  - after a split: nothing (--after_split none), a new anchor = the trained global model with the Psi of every client
    computed again (reanchor), or a cannot-link between the clients of the two sides (cannot_link).
With --split 0 the clustering and the training are those of StoCFL-FCC+CFL.py; the extra logs are used to calibrate
eps1 and eps2. The split needs every client in every round (num_per_round = n, no --drop).
"""
import argparse
import importlib.util
import os
import random
import time
from copy import deepcopy

import numpy as np
import torch
from fedlab.utils import SerializationTool, Aggregators, Logger

from datasets import RotatedMNIST, RotatedCIFAR10Partitioner
from functional import cluster_center, dt_matrix, parse_matrix, evaluate_recall, setup_seed
from models.cnn import CNN_CIFAR10
from models.linear import SimpleLinear
from trainer import RotatedMNISTTrainer

# StoCFL-FCC+CFL.py cannot be imported by name (hyphen and plus): load it as a module; its __main__ block does not run
_spec = importlib.util.spec_from_file_location(
    "stocfl_fcc_cfl", os.path.join(os.path.dirname(os.path.abspath(__file__)), "StoCFL-FCC+CFL.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def bipartition(S):
    # Algorithm 1 of the CFL paper, as Server.cluster_clients in clustered-federated-learning/fl_devices.py:
    # merge along the most similar pairs until two clusters remain; c1 and c2 are positions in S
    M = len(S)
    clusters = [{i} for i in range(M)]
    for s in np.argsort(-S, axis=None, kind="stable"):
        i1, i2 = int(s) // M, int(s) % M
        c_tmp = [c for c in clusters if i1 in c or i2 in c]
        clusters = [c for c in clusters if c not in c_tmp] + [set().union(*c_tmp)]
        if len(clusters) == 2:
            break
    c1, c2 = [np.array(sorted(c)) for c in clusters]
    return c1, c2


def cosine_matrix(vectors):
    X = torch.stack(vectors).double()
    X = X / X.norm(dim=1, keepdim=True)
    return (X @ X.T).numpy()


class SplitServer(_base.StandaloneServer):
    def __init__(self, model, cuda, client_trainer, args):
        super().__init__(model, cuda, client_trainer, args)
        n = self.client_num
        self.separated = np.zeros((n, n), dtype=bool) # clients put apart by an accepted split
        self.forbidden = np.zeros((n, n), dtype=bool) # cannot-link, only with --after_split cannot_link
        self.events = {"splits": [], "remerges": [], "blocked": [], "reanchors": []}
        self.psi_cos = None
        self.psi_cos_log = [] # cosine between the Psi of the clients, at the first observation and after each reanchor
        self.round = 0

    def main(self):
        cluster_log = []
        accuracy_log = []
        availability_log = []
        client_accuracy_log = [] # per round: accuracy of each client's cluster model on its group, and of the global model per group
        norms_log = [] # per round: the CFL criterion inputs of each cluster with 2+ members
        for round in range(self.args.com_round):
            self.round = round
            if self.args.drop > 0:
                up = self.availability.step()
                available = [c for c in self.client_id if up[c]]
                unavailable = [c for c in self.client_id if not up[c]]
                self.args.exp_logger.info("Round {}/{}, unavailable {}".format(round, self.args.com_round, unavailable))
                availability_log.append(unavailable)
                torch.save(availability_log, "{}/availability.pkl".format(self.args.dir))
                cid_this_round = sorted(random.sample(available, min(self.args.num_per_round, len(available))))
            else:
                cid_this_round = sorted(random.sample(self.client_id, self.args.num_per_round))
            self.args.exp_logger.info("Starting round {}/{}, client id this round {}".format(round, self.args.com_round, cid_this_round))

            # anchor move (psi.pkl is not written: ~6.5 MB per client in every round; the cosines go to psi_cos.pkl)
            unobserved = [cid for cid in cid_this_round if cid not in self.psi.keys()]
            movements = self.client_trainer.observe(unobserved, self.anchor)
            for cid, move in zip(unobserved, movements):
                self.psi[cid] = move
            if unobserved:
                self.update_psi_cos(round, "observe")

            # cluster
            sampled_cluster = sorted({self.find_client_cluster[i] for i in cid_this_round})
            cluster_movements = [cluster_center(self.psi, self.find_cluster_content[clu_id]) for clu_id in sampled_cluster]
            self.inter_cluster_union(sampled_cluster, cluster_movements)
            self.get_cluster()
            cluster_log.append(deepcopy(self.find_cluster_content))
            torch.save(cluster_log, "{}/cluster.pkl".format(self.args.dir))

            # clustered federated optimization
            if self.args.train and not cid_this_round:
                accuracy_log.append({"cluster": [], "global": [], "cluster_recall": [], "global_recall": []})
                torch.save(accuracy_log, "{}/accuracy.pkl".format(self.args.dir))
            elif self.args.train:
                for id in cid_this_round:
                    if self.find_client_cluster[id] not in self.cluster_parameters.keys():
                        self.cluster_parameters[self.find_client_cluster[id]] = deepcopy(self.anchor)
                cluster_models = [self.cluster_parameters[self.find_client_cluster[i]] for i in cid_this_round]
                updated_cmodels, gmodels = self.client_trainer.train(cid_this_round, cluster_models, self.gmodel)
                # dW of each client on its cluster model (the CFL signal); train returns new tensors
                updates = {cid: updated_cmodels[i] - cluster_models[i] for i, cid in enumerate(cid_this_round)}

                # update global models
                self.gmodel = Aggregators.fedavg_aggregate(gmodels)

                # update cluster models
                g_test, g_recall = [], []
                accuracy = {"cluster":[], "global": None, "cluster_recall": [], "global_recall": None}
                sampled_cluster, updates_bucket = self.bucket(cid_this_round, updated_cmodels)
                for cluster, cluster_updates in zip(sampled_cluster, updates_bucket):
                    self.cluster_parameters[cluster] = Aggregators.fedavg_aggregate(cluster_updates)
                    SerializationTool.deserialize_model(self._model, self.cluster_parameters[cluster])

                    cluster_content = self.find_cluster_content[cluster]
                    test_loader = self.client_trainer.get_test_dataloader(int(cluster_content[0]*self.args.k/self.args.n))
                    loss, acc, recall = evaluate_recall(self._model, torch.nn.CrossEntropyLoss(), test_loader)
                    self.args.exp_logger.info("Round {}, Cluster {} - Global Test loss: {:.4f}, acc: {:.4f}".format(round, cluster, loss, acc))
                    accuracy["cluster"].append(acc)
                    accuracy["cluster_recall"].append(recall)

                    # global test
                    SerializationTool.deserialize_model(self._model, self.gmodel)
                    _, acc, recall = evaluate_recall(self._model, torch.nn.CrossEntropyLoss(), test_loader)
                    g_test.append(acc)
                    g_recall.append(recall)
                accuracy["global"] = g_test
                accuracy["global_recall"] = g_recall
                accuracy_log.append(accuracy)
                torch.save(accuracy_log, "{}/accuracy.pkl".format(self.args.dir))
                self.args.exp_logger.info("Round {}, Global acc: {}".format(round, g_test))

                client_accuracy_log.append(self.evaluate_clients())
                torch.save(client_accuracy_log, "{}/accuracy_clients.pkl".format(self.args.dir))
                norms = self.cluster_norms(updates)
                norms_log.append(norms)
                torch.save(norms_log, "{}/norms.pkl".format(self.args.dir))
                if self.args.split:
                    self.split_step(round, norms, updates)
            torch.save(self.events, "{}/split_events.pkl".format(self.args.dir))

    def current(self, i):
        # cluster that holds cluster i now (i may have been absorbed earlier in the round), as in unite
        return i if i in self.find_cluster_content[i] else self.find_client_cluster[i]

    def inter_cluster_union(self, sampled_cluster, cluster_directions):
        # StandaloneServer.inter_cluster_union, plus: a union that puts together clients separated by a split
        # is recorded (remerge) and, with cannot_link, skipped
        if len(sampled_cluster) <= 1:
            return
        M = dt_matrix(cluster_directions)
        sorted_key, result = parse_matrix(M, sampled_cluster, descending=True)

        filename = "{}/cos_rec.log".format(self.args.dir)
        if os.path.exists(filename):
            os.remove(filename)
        matrix_logger = Logger("matrix",filename)
        for key in sorted_key:
            matrix_logger.info("%s:%f" % (key,result[key]))

        for key in sorted_key:
            cida, cidb = int(key.split(',')[0]), int(key.split(',')[1]) # cluster id
            if result[key] > self.tau:
                a, b = self.current(cida), self.current(cidb)
                if a == b:
                    continue
                pairs = np.ix_(self.find_cluster_content[a], self.find_cluster_content[b])
                if self.forbidden[pairs].any():
                    self.events["blocked"].append({"round": self.round, "clusters": [a, b], "cos": result[key]})
                    continue
                if self.separated[pairs].any():
                    self.events["remerges"].append({"round": self.round, "clusters": [a, b], "cos": result[key],
                                                    "pairs": int(self.separated[pairs].sum())})
                    self.args.exp_logger.info("Round {}, remerge of clusters {} and {} (cos {:.4f})".format(self.round, a, b, result[key]))
                self.unite(cida, cidb)
            else:
                break

    def update_psi_cos(self, round, why):
        ids = sorted(self.psi.keys())
        C = np.full((self.client_num, self.client_num), np.nan)
        C[np.ix_(ids, ids)] = cosine_matrix([self.psi[i] for i in ids])
        self.psi_cos = C
        self.psi_cos_log.append({"round": round, "why": why, "cos": C.astype(np.float32)})
        torch.save(self.psi_cos_log, "{}/psi_cos.pkl".format(self.args.dir))

    def psi_min(self, members):
        sub = self.psi_cos[np.ix_(members, members)]
        return sub[~np.eye(len(members), dtype=bool)].min()

    def cluster_norms(self, updates):
        # inputs of the CFL criterion for every cluster with 2+ members in the round
        out = []
        for c, members in self.find_cluster_content.items():
            part = sorted(i for i in members if i in updates)
            if len(part) < 2:
                continue
            dW = torch.stack([updates[i] for i in part])
            out.append({"cluster": c, "members": part, "mean_norm": dW.mean(dim=0).norm().item(),
                        "max_norm": dW.norm(dim=1).max().item(), "psi_min": float(self.psi_min(members))})
        return out

    def split_step(self, round, norms, updates):
        accepted = False
        for entry in norms:
            if entry["psi_min"] > self.tau: # every pair of members would merge alone: nothing to check
                continue
            if not (entry["mean_norm"] < self.args.eps1 and entry["max_norm"] > self.args.eps2):
                continue
            c, part = entry["cluster"], entry["members"]
            S = cosine_matrix([updates[i] for i in part])
            c1, c2 = bipartition(S)
            alpha = float(S[np.ix_(c1, c2)].max())
            ok = self.args.gamma_max < np.sqrt((1 - alpha) / 2)
            side1, side2 = [part[j] for j in c1], [part[j] for j in c2]
            self.events["splits"].append({"round": round, "cluster": c, "sides": [side1, side2], "alpha_cross_max": alpha,
                                          "mean_norm": entry["mean_norm"], "max_norm": entry["max_norm"], "accepted": bool(ok)})
            self.args.exp_logger.info("Round {}, Cluster {} - CFL split {}: {} | {} (alpha_cross_max {:.4f})".format(
                round, c, "accepted" if ok else "rejected", side1, side2, alpha))
            if ok:
                self.split(c, side1, side2)
                accepted = True
        if accepted:
            self.get_cluster()
            if self.args.after_split == "reanchor":
                self.reanchor(round)

    def split(self, c, side1, side2):
        # the side with client c keeps the id c; the other gets its smallest client id, whose slot is empty (invariant 1)
        keep, other = (side1, side2) if c in side1 else (side2, side1)
        new = min(other)
        assert not self.find_cluster_content[new], "cluster {} is not empty".format(new)
        self.find_cluster_content[c] = sorted(keep)
        self.find_cluster_content[new] = sorted(other)
        for i in other:
            self.find_client_cluster[i] = new
        if c in self.cluster_parameters.keys():
            self.cluster_parameters[new] = deepcopy(self.cluster_parameters[c])
        self.separated[np.ix_(keep, other)] = True
        self.separated[np.ix_(other, keep)] = True
        if self.args.after_split == "cannot_link":
            self.forbidden[np.ix_(keep, other)] = True
            self.forbidden[np.ix_(other, keep)] = True

    def reanchor(self, round):
        # "new global model": the trained global model becomes the anchor, and every observed client gets its Psi again
        self.anchor = deepcopy(self.gmodel)
        ids = sorted(self.psi.keys())
        for cid, move in zip(ids, self.client_trainer.observe(ids, self.anchor)):
            self.psi[cid] = move
        self.update_psi_cos(round, "reanchor")
        self.events["reanchors"].append({"round": round})
        self.args.exp_logger.info("Round {}, reanchor: Psi of {} clients computed again at the global model".format(round, len(ids)))

    def evaluate_clients(self):
        # accuracy of each client's cluster model on the test set of the client's group (a cluster that mixes groups is
        # tested on each of them), and of the global model on each group
        group = lambda cid: int(cid * self.args.k / self.args.n)
        crit = torch.nn.CrossEntropyLoss()
        cluster_acc = [None] * self.client_num
        for c, members in self.find_cluster_content.items():
            if not members or c not in self.cluster_parameters.keys():
                continue
            SerializationTool.deserialize_model(self._model, self.cluster_parameters[c])
            for g in sorted({group(i) for i in members}):
                _, acc, _ = evaluate_recall(self._model, crit, self.client_trainer.get_test_dataloader(g))
                for i in members:
                    if group(i) == g:
                        cluster_acc[i] = acc
        SerializationTool.deserialize_model(self._model, self.gmodel)
        global_acc = [evaluate_recall(self._model, crit, self.client_trainer.get_test_dataloader(g))[1] for g in range(self.args.k)]
        return {"cluster": cluster_acc, "global": global_acc}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StoCFL with an experimental CFL split")
    # same arguments as StoCFL-FCC+CFL.py
    parser.add_argument("--n", type=int)
    parser.add_argument("--com_round", type=int)
    parser.add_argument("--num_per_round", type=int)
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--lr", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--mu", type=float, default=0.05)
    parser.add_argument("--obbs", type=int, default=None)
    parser.add_argument("--tau", type=float, default=0.5)
    parser.add_argument("--train", type=int, default=1)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--dataset", type=str, default="cifar")
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--drop", type=float, default=0.0)
    parser.add_argument("--drop_rounds", type=int, default=1)
    parser.add_argument("--process", type=int, default=0)
    # split
    parser.add_argument("--split", type=int, default=1) # 0 = no split (StoCFL-FCC+CFL.py plus the extra logs)
    parser.add_argument("--after_split", type=str, default="none", choices=["none", "reanchor", "cannot_link"])
    parser.add_argument("--eps1", type=float, default=None) # CFL: split only if ||mean dW|| < eps1
    parser.add_argument("--eps2", type=float, default=None) # CFL: and max ||dW_i|| > eps2
    parser.add_argument("--gamma_max", type=float, default=0.5) # CFL: accept if gamma_max < sqrt((1 - alpha_cross_max) / 2)
    args = parser.parse_args()
    args.dirichlet_alpha = None # the rotated partition only

    setup_seed(args.seed)

    default_k = 4 if args.dataset == "mnist" else 2
    if args.k is None:
        args.k = default_k
    assert args.dataset == "mnist" or args.k == 2, "cifar only supports k=2"
    assert args.n % args.k == 0, "n must be divisible by k"
    assert 0 <= args.drop < 1, "drop must be in [0, 1)"
    assert args.drop_rounds >= 1, "drop_rounds must be >= 1"
    assert args.drop == 0 or args.num_per_round <= args.n, "num_per_round must be <= n"
    assert args.train or not args.split, "the split needs --train 1 (the CFL signal is the update of the cluster model)"
    assert not args.split or (args.eps1 is not None and args.eps2 is not None), "the split needs --eps1 and --eps2"
    assert not args.split or (args.num_per_round == args.n and args.drop == 0), "the split needs every client in every round"
    k_tag = "" if args.k == default_k else "_k{}".format(args.k)

    args.root = "./datasets/{}/".format(args.dataset)
    args.save_dir = "./datasets/rotated_{}_{}_{}{}/".format(args.dataset, args.n, args.seed, k_tag)

    if args.process:
        print("Preprocessing datasets...")
        if args.dataset == "mnist":
            RotatedMNIST(args.root, args.save_dir).pre_process(thetas=[360 * i / args.k for i in range(args.k)], shards=args.n // args.k)
        if args.dataset == "cifar":
            RotatedCIFAR10Partitioner(args.root, args.save_dir).pre_process(shards=int(args.n/2))

    model = SimpleLinear() if args.dataset == "mnist" else CNN_CIFAR10()
    trainer = RotatedMNISTTrainer(deepcopy(model), args, cuda=torch.cuda.is_available())

    # the folder has tau, the variant and the seconds: runs with different tau in the same minute do not mix
    args.time_stamp = time.strftime('%m-%d-%H:%M:%S', time.localtime())
    drop_tag = "-drop{}-r{}".format(args.drop, args.drop_rounds) if args.drop > 0 else ""
    split_tag = "-split-{}".format(args.after_split) if args.split else "-nosplit"
    dir = "./logs/runs-split-rotated-{}-n{}-p{}-seed{}-lambda{}{}{}-tau{}{}-time-{}".format(
        args.dataset, args.n, args.num_per_round, args.seed, args.mu, k_tag.replace("_", "-"), drop_tag, args.tau, split_tag, args.time_stamp)
    os.makedirs(dir, exist_ok=True)
    args.exp_logger = Logger("StoCFL", "{}/rotated_{}.log".format(dir, args.dataset))
    args.exp_logger.info(str(args))
    args.dir = dir
    server = SplitServer(deepcopy(model), torch.cuda.is_available(), trainer, args)
    server.main()
