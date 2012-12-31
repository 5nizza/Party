import unittest
import os
from interfaces.spec import SpecProperty
from optimizations import strengthen, localize
from parsing.interface import QuantifiedSignal, ForallExpr, UnaryOp, BinOp, Bool, Signal
from translation2uct.ltl2automaton import Ltl2UCW


def _get_is_true(signal_name:str, *binding_indices):
    if len(binding_indices) == 0:
        signal = Signal(signal_name)
    else:
        signal = QuantifiedSignal(signal_name, binding_indices)
    return BinOp('=', signal, Bool(True))


class TestStrengthen(unittest.TestCase):
    def _get_converter(self):
        me_abs_path = str(os.path.abspath(__file__))
        root_dir_toks = me_abs_path.split(os.sep)[:-1]
        root_dir = os.sep.join(root_dir_toks)
        ltl2ba_path = root_dir + '/../lib/ltl3ba/ltl3ba-1.0.1/ltl3ba'

        return Ltl2UCW(ltl2ba_path)


    def test_strengthen1(self):
        """
        Forall(i) GFa_i -> Forall(j) G(b_j)
        replaced by
        'safety': Forall(j) G(b_j)
        'liveness': []
        """

        a_i, b_j = QuantifiedSignal('a', ('i',)), QuantifiedSignal('b', ('j',))

        liveness_ass = ForallExpr(['i'], UnaryOp('G', UnaryOp('F', a_i)))
        safety_gua = ForallExpr(['j'], UnaryOp('G', b_j))

        property = SpecProperty([liveness_ass], [safety_gua])

        safety_properties, liveness_properties = strengthen([property], self._get_converter())

        assert len(liveness_properties) == 0, str(liveness_properties)
        assert len(safety_properties) == 1, str(safety_properties)

        actual = safety_properties[0]
        expected = SpecProperty([], [safety_gua])
        assert str(actual) == str(expected), str(actual) + ' vs ' + str(expected)


    def test_strengthen2(self):
        """
        Forall(i) GFa_i -> Forall(j) GF(b_j)
        is left as it is
        """
        a_i, b_j = QuantifiedSignal('a', ('i',)), QuantifiedSignal('b', ('j',))

        liveness_ass = ForallExpr(['i'], UnaryOp('G', UnaryOp('F', a_i)))
        liveness_gua = ForallExpr(['j'], UnaryOp('G', UnaryOp('F', b_j)))

        property = SpecProperty([liveness_ass], [liveness_gua])

        safety_properties, liveness_properties = strengthen([property], self._get_converter())

        assert len(liveness_properties) == 1, str(liveness_properties)
        assert len(safety_properties) == 0, str(safety_properties)

        actual = liveness_properties[0]
        expected = property
        assert str(actual) == str(expected), str(actual) + ' vs ' + str(expected)


    def test_strengthen2(self):
        """
        Forall(i) GFa_i and G(b_i)  ->  Forall(j) GF(c_j) and G(d_j)
        replaced by
        'liveness': Forall(i) GFa_i and G(b_i)  ->  Forall(j) GF(c_j)
        and
        'safety': Forall(i) G(b_i)  ->  Forall(j) G(d_j)
        """

        a_i, b_i = QuantifiedSignal('a', ('i',)), QuantifiedSignal('b', ('i',))
        c_j, d_j = QuantifiedSignal('c', ('j',)), QuantifiedSignal('d', ('j',))

        ass = ForallExpr(['i'],
            BinOp('*',
                UnaryOp('G', UnaryOp('F', a_i)),
                UnaryOp('G', b_i)
            ))
        gua = ForallExpr(['j'],
            BinOp('*',
                UnaryOp('G', UnaryOp('F', c_j)),
                UnaryOp('G', d_j)))

        property = SpecProperty([ass], [gua])

        safety_properties, liveness_properties = strengthen([property], self._get_converter())

        assert len(liveness_properties) == 1, str(liveness_properties)
        assert len(safety_properties) == 1, str(safety_properties)


        expected_liveness_gua = ForallExpr(['j'], UnaryOp('G', UnaryOp('F', c_j)))

        #: :type: SpecProperty
        liveness_prop = liveness_properties[0]
        assert str(liveness_prop.assumptions) == str([ass]), str(liveness_prop)
        assert str(liveness_prop.guarantees) == str([expected_liveness_gua])


        safety_prop = safety_properties[0]
        expected_safety_ass = ForallExpr(['i'], UnaryOp('G', b_i))
        expected_safety_gua = ForallExpr(['j'], UnaryOp('G', d_j))
        expected_safety_prop = SpecProperty([expected_safety_ass], [expected_safety_gua])
        assert str(expected_safety_prop) == str(safety_prop), str(safety_prop)


    def test_strengthen3(self):
        """ Forall(i,j) GFa_i * GFb_i_j * Gc_i_j -> Forall(k,m) GF(d_k_m) * G(e_k)
        replaced by
        'safety':   Forall(i) Gc_i  ->  Forall(k) G(e_k)
        'liveness': Forall(i,j) GFa_i * GFb_i_j * Gc_i  ->  Forall(k,m) GF(d_k_m)
        """
        assert 0, 'todo'


class TestReduceQuantifiers(unittest.TestCase):
    def test_reduce(self):
        """ Forall(i,j) Ga_i -> Forall(k,m,l) Gb_k_m
        replaced by
        Forall(i) Ga_i -> Forall(k,m) Gb_k_m
        """

        a_i = _get_is_true('a', 'i')
        b_k_m = _get_is_true('b', 'k', 'm')

        ass = ForallExpr(['i','j'], UnaryOp('G', a_i))
        gua = ForallExpr(['k','m','l'], UnaryOp('G', b_k_m))
        property = SpecProperty([ass], [gua])

        actual_p = _reduce_quantifiers(property)
        expected_p = SpecProperty([ForallExpr(['i'], a_i)], [ForallExpr(['k', 'm'], b_k_m)])

        assert str(actual_p) == str(expected_p), str(actual_p)


class TestLocalize(unittest.TestCase):
    def test_localize_one_ass_one_gua(self):
        """ forall(i) a_i -> forall(j) b_j
         replaced by
            forall(i) (a_i -> b_i)
        """

        a_i_is_true, a_j_is_true, b_j_is_true, b_i_is_true = _get_is_true('a', 'i'), _get_is_true('a', 'j'),\
                                                             _get_is_true('b', 'j'), _get_is_true('b', 'i')

        prop = SpecProperty([ForallExpr(['i'], a_i_is_true)], [ForallExpr(['j'], b_j_is_true)])

        localized_prop = localize(prop)
        expected_prop_i = SpecProperty([Bool(True)], [ForallExpr(['i'], BinOp('->', a_i_is_true, b_i_is_true))])
        expected_prop_j = SpecProperty([Bool(True)], [ForallExpr(['j'], BinOp('->', a_j_is_true, b_j_is_true))])

        expected_prop_str_i = str(expected_prop_i)
        expected_prop_str_j = str(expected_prop_j)
        localized_prop_str = str(localized_prop)

        assert localized_prop_str == expected_prop_str_i\
        or localized_prop_str == expected_prop_str_j, str(localized_prop_str)


    def test_localize_two_ass_one_gua(self):
        """
        forall(i,j) a_i_j ->  forall(i) b_i
        replaced by
        forall(i,j) (a_i_j ->  b_i)
        """

        a_i_j_is_true, b_j_is_true = _get_is_true('a', 'i', 'j'), _get_is_true('b', 'j')
        b_i_is_true = _get_is_true('b', 'i')

        prop = SpecProperty(
            [ForallExpr(['i', 'j'], a_i_j_is_true)],
            [ForallExpr(['j'], b_j_is_true)])

        localized_prop = localize(prop)
        expected_prop_i_j1 = SpecProperty([Bool(True)], [ForallExpr(['i', 'j'], BinOp('->', a_i_j_is_true, b_j_is_true))])
        expected_prop_i_j2 = SpecProperty([Bool(True)], [ForallExpr(['i', 'j'], BinOp('->', a_i_j_is_true, b_i_is_true))])

        assert str(localized_prop) == str(expected_prop_i_j1) or\
               str(localized_prop) == str(expected_prop_i_j2),\
        str(localized_prop)


    def test_localize_one_ass_two_gua(self):
        """
        forall(i,j) a_i ->  forall(i,j) b_i_j
        replaced by
        forall(i,j) (a_i ->  b_i_j)
        """

        a_i_is_true, a_k_is_true, a_j_is_true = _get_is_true('a', 'i'), _get_is_true('a', 'k'), _get_is_true('a', 'j')
        b_k_j_is_true = _get_is_true('b', 'k', 'j')

        prop = SpecProperty(
            [ForallExpr(['i'], a_i_is_true)],
            [ForallExpr(['k', 'j'], b_k_j_is_true)])

        localized_prop = localize(prop)
        expected_prop_k_j1 = SpecProperty([Bool(True)], [ForallExpr(['k', 'j'], BinOp('->', a_k_is_true, b_k_j_is_true))])
        expected_prop_k_j2 = SpecProperty([Bool(True)], [ForallExpr(['k', 'j'], BinOp('->', a_j_is_true, b_k_j_is_true))])

        assert str(localized_prop) == str(expected_prop_k_j1)\
        or str(localized_prop) == str(expected_prop_k_j2), str(localized_prop)


    def test_localize_zero_ass(self):
        """
        true -> forall(i) b_i
        replaced by
        forall(i) (true -> b_i)
        """

        b_i_is_true = _get_is_true('b', 'i')

        prop = SpecProperty(
            [Bool(True)],
            [ForallExpr(['i'], b_i_is_true)])

        localized_prop = localize(prop)
        expected_prop = SpecProperty([Bool(True)], [ForallExpr(['i'], BinOp('->', Bool(True), b_i_is_true))])

        assert str(localized_prop) == str(expected_prop), str(localized_prop)









