import argparse
import sys

from mlpipeline.mymodule import fizzbuzz


def main() -> None:
    parser = argparse.ArgumentParser(description="mlp")
    parser.add_argument("num", type=int, help="A number")
    args = parser.parse_args()
    sys.stdout.write(f"{fizzbuzz(args.num)}\n")
