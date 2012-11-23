from io import StringIO
import logging
import tempfile

from helpers.logging import log_entrance
from helpers.python_ext import StrAwareList, FileAsStringEmulator
from synthesis.generic_smt_encoder import GenericEncoder
from synthesis.local_en_process_impl import SyncImpl
from synthesis.par_impl import ParImpl
from synthesis.smt_helper import comment
from synthesis.smt_logic import UFLIA
from synthesis.z3 import Z3


@log_entrance(logging.getLogger(), logging.INFO)
def search(logic,
           global_automata_nof_processes_pairs,
           local_automaton,
           anon_inputs, anon_outputs,
                        local_bounds,
                        z3solver,
                        sched_id_prefix,
                        active_var_name,
                        sends_anon_var_name,
                        has_tok_var_prefix,
                        sends_prev_var_name,
                        smt_file_name):
    logger = logging.getLogger()

    sys_state_type = 'T'
    tau_name = 'tau'

    for bound in local_bounds:
        logger.info('trying size %i', bound)

        smt_file = open(smt_file_name+'_'+str(bound), 'w')
        query_lines = StrAwareList(FileAsStringEmulator(smt_file))

        encoder=impl=None
        for i, (automaton, nof_processes) in enumerate(global_automata_nof_processes_pairs):
            counters_postfix = sys_intern_funcs_postfix = '_'+str(i)
            spec_states_type = 'Q'+str(i)

            encoder = GenericEncoder(logic, spec_states_type, counters_postfix)

            impl = ParImpl(automaton, anon_inputs, anon_outputs, nof_processes, bound,
                sched_id_prefix, active_var_name, sends_anon_var_name, sends_prev_var_name, has_tok_var_prefix,
                sys_state_type,
                tau_name,
                sys_intern_funcs_postfix)

            if i is 0:
                encoder.encode_headers(query_lines)
                encoder.encode_sys_model_functions(impl, query_lines)

                query_lines += comment('local_encoder')

                local_impl = SyncImpl(local_automaton, anon_inputs, anon_outputs,
                    bound,
                    sys_state_type,
                    has_tok_var_prefix, sends_anon_var_name, sends_prev_var_name,
                    tau_name,
                    impl.init_states[0])

                local_encoder = GenericEncoder(logic, 'LQ', 'l')
                local_encoder.encode_run_graph_headers(local_impl, query_lines)
                local_encoder.encode_run_graph(local_impl, query_lines)

            query_lines += comment('global_encoder' + sys_intern_funcs_postfix)

            encoder.encode_sys_aux_functions(impl, query_lines)
            encoder.encode_run_graph_headers(impl, query_lines)
            encoder.encode_run_graph(impl, query_lines)

        encoder.encode_footings(impl, query_lines)

        logger.info('smt query has %i lines', len(query_lines))

        smt_file.close()

        status, data_lines = z3solver.solve_file(smt_file.name)

        if status == Z3.SAT:
            return encoder.parse_model(data_lines, impl)

    return None
