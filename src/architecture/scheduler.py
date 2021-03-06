from interfaces.parser_expr import BinOp, UnaryOp, ForallExpr, QuantifiedSignal, Number


SCHED_ID_PREFIX = 'sch'
ACTIVE_NAME = 'active'


class InterleavingScheduler:
    """ Each moment only one process is active. """

    _FAIR_SCHED_NAME = 'fair_scheduling'

    @property
    def assumptions(self):
        return [ForallExpr(['i'],
                           UnaryOp('G', UnaryOp('F',
                                                BinOp('=',
                                                      QuantifiedSignal(self._FAIR_SCHED_NAME, 'i'),
                                                      Number(1)))))]

    def is_scheduler_signal(self, signal:QuantifiedSignal) -> bool:
        return signal.name == self._FAIR_SCHED_NAME