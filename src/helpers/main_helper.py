from lib2to3.pytree import convert
import logging
import os
import sys
from synthesis.smt_logic import Logic

from synthesis.solvers import Z3_Smt_NonInteractive_ViaFiles, Z3_Smt_Interactive
from translation2uct.ltl2automaton import Ltl2UCW


def get_root_dir() -> str:
    #make paths independent of current working directory
    rel_path = str(os.path.relpath(__file__))
    bosy_dir_toks = ['./'] + rel_path.split(os.sep)   # abspath returns 'windows' (not cygwin) path
    root_dir = ('/'.join(bosy_dir_toks[:-1]) + '/../../')   # root dir is two levels up compared to helpers/.
    return root_dir


def setup_logging(verbose):
    level = None
    if verbose is 0:
        level = logging.INFO
    elif verbose >= 1:
        level = logging.DEBUG

    logging.basicConfig(format="%(asctime)-10s%(message)s",
                        datefmt="%H:%M:%S",
                        level=level,
                        stream=sys.stdout)

    return logging.getLogger(__name__)


def create_spec_converter_z3(logger:logging.Logger,
                             logic:Logic,
                             is_incremental:bool,
                             smt_tmp_files_prefix:str=None):
    """ Return ltl to automaton converter, Z3 solver """
    assert smt_tmp_files_prefix or is_incremental

    from config import z3_path, ltl3ba_path

    if is_incremental:
        solver = Z3_Smt_Interactive(logic, z3_path, logger)
    else:
        solver = Z3_Smt_NonInteractive_ViaFiles(smt_tmp_files_prefix, z3_path, logic, logger)

    converter = Ltl2UCW(ltl3ba_path)

    return converter, solver


def remove_files_prefixed(file_prefix:str):
    """ Remove files from the current directory prefixed with a given prefix """
    for f in os.listdir():
        if f.startswith(file_prefix):
            os.remove(f)
