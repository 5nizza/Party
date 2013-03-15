import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

import argparse
from tests.common import run_benchmark


_REALIZABLE = [
    "parameterized/full_arbiter.ltl --cutoff 2 --size 3 --opt strength",
    "parameterized/full_arbiter.ltl --cutoff 3 --size 3 --opt strength",

    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 3 --opt strength",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 3 --opt strength",


    "parameterized/full_arbiter.ltl --cutoff 2 --size 3 --opt async_hub",
    "parameterized/full_arbiter.ltl --cutoff 3 --size 3 --opt async_hub",

    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 3 --opt async_hub",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 3 --opt async_hub",


    "parameterized/full_arbiter.ltl --cutoff 2 --size 3 --opt sync_hub",
    "parameterized/full_arbiter.ltl --cutoff 3 --size 3 --opt sync_hub"
]

_UNREALIZABLE = [
    "parameterized/full_arbiter.ltl --cutoff 2 --size 2 --opt strength",
    "parameterized/full_arbiter.ltl --cutoff 3 --size 2 --opt strength",

    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 2 --opt strength",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 2 --opt strength",


    "parameterized/full_arbiter.ltl --cutoff 2 --size 2 --opt async_hub",
    "parameterized/full_arbiter.ltl --cutoff 3 --size 2 --opt async_hub",

    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 2 --opt async_hub",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 2 --opt async_hub",


    "parameterized/full_arbiter.ltl --cutoff 2 --size 2 --opt sync_hub",
    "parameterized/full_arbiter.ltl --cutoff 3 --size 2 --opt sync_hub",

    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 2 --opt sync_hub",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 2 --opt sync_hub"
]


_REALIZABLE_SUBSET = [
    "parameterized/full_arbiter.ltl --cutoff 3 --size 3 --opt strength",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 3 --opt strength",

    "parameterized/full_arbiter.ltl --cutoff 3 --size 3 --opt async_hub",
    "parameterized/pnueli_arbiter.ltl --cutoff 3 --size 3 --opt sync_hub"
]


_UNREALIZABLE_SUBSET = [
    "parameterized/full_arbiter.ltl --cutoff 2 --size 2 --opt strength",
    "parameterized/full_arbiter.ltl --cutoff 2 --size 2 --opt async_hub",
    "parameterized/full_arbiter.ltl --cutoff 2 --size 2 --opt sync_hub",

    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 2 --opt strength",
    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 2 --opt async_hub",
    "parameterized/pnueli_arbiter.ltl --cutoff 2 --size 2 --opt sync_hub",
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parametrized Synthesis Tool for token rings architecture')
    parser.add_argument('--nonstop', action='store_true', required=False, default=False,
                        help="don't stop on error")
    parser.add_argument('--extensive', action='store_true', required=False, default=False,
                        help="extensive testing (consider more sizes and more cutoffs)")

    args = parser.parse_args(sys.argv[1:])
    print(args)

    realizable = _REALIZABLE_SUBSET
    unrealizable = _UNREALIZABLE_SUBSET

    if args.extensive:
        realizable = _REALIZABLE
        unrealizable = _UNREALIZABLE

    all_passed = True
    for benchmark in realizable + unrealizable:
        result = run_benchmark('src/p_bosy.py', benchmark, benchmark in realizable)
        all_passed &= result

        if not args.nonstop and result is False:
            exit(1)

    print('-'*80)
    print(['SOME TESTS FAILED', 'ALL TESTS PASSED'][all_passed])