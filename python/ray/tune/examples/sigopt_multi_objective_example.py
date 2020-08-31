"""This test checks that SigOpt is functional.

It also checks that it is usable with a separate scheduler.
"""
import time

import ray
import numpy as np
from ray import tune
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.suggest.sigopt import SigOptSearch

np.random.seed(0)
vector1 = np.random.normal(0, 0.1, 100)
vector2 = np.random.normal(0, 0.1, 100)

def evaluate(w1, w2):
    total = w1 * vector1 + w2 * vector2
    return total.mean(), total.std()


def easy_objective(config):
    # Hyperparameters
    w1 = config["w1"]
    w2 = config["total_weight"] - w1

    average, std = evaluate(w1, w2)
    tune.report(average=average, std=std)
    time.sleep(0.1)


if __name__ == "__main__":
    import argparse
    import os

    assert "SIGOPT_KEY" in os.environ, \
        "SigOpt API key must be stored as environment variable at SIGOPT_KEY"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    space = [
        {
            "name": "w1",
            "type": "double",
            "bounds": {
                "min": 0,
                "max": 1
            },
        },
    ]

    config = {
        "num_samples": 10 if args.smoke_test else 1000,
        "config": {
            "total_weight": 1
        }
    }

    algo = SigOptSearch(
        space,
        name="SigOpt Example Multi Objective Experiment",
        observation_budget=10 if args.smoke_test else 1000,
        max_concurrent=1,
        metric=["average", "std"],
        mode=["max", "min"])
    scheduler = AsyncHyperBandScheduler(metric="mean_loss", mode="min")
    tune.run(
        easy_objective,
        name="my_exp",
        search_alg=algo,
        scheduler=scheduler,
        **config)
