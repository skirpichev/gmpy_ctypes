"""Implements gmpy2-compatible interfaces."""

import ctypes
import ctypes.util
import numbers


# find the GMP library
_libgmp_path = ctypes.util.find_library('gmp')
if not _libgmp_path:
    raise EnvironmentError('Unable to find libgmp')
_libgmp = ctypes.CDLL(_libgmp_path)


#
# GNU MP structures
#
#  - TODO: choose between different definitions of these structures based on
#  checking library/arch. For example, different library configuration options
#  and 32-bit/64-bit systems.
#


class _c_mpz_struct(ctypes.Structure):
    _fields_ = [('_mp_alloc', ctypes.c_int),
                ('_mp_size', ctypes.c_int),
                ('_mp_d', ctypes.POINTER(ctypes.c_ulonglong))]


class _c_mpq_struct(ctypes.Structure):
    _fields_ = [('_mp_num', _c_mpz_struct),
                ('_mp_den', _c_mpz_struct)]


#
# Function references into MP library
# ------------------------------------

# Gnu MP integer routines
_MPZ_init = _libgmp.__gmpz_init
_MPZ_clear = _libgmp.__gmpz_clear
_MPZ_add = _libgmp.__gmpz_add
_MPZ_sub = _libgmp.__gmpz_sub
_MPZ_mul = _libgmp.__gmpz_mul
_MPZ_div = _libgmp.__gmpz_fdiv_q
_MPZ_mod = _libgmp.__gmpz_fdiv_r
_MPZ_and = _libgmp.__gmpz_and
_MPZ_ior = _libgmp.__gmpz_ior
_MPZ_xor = _libgmp.__gmpz_xor
_MPZ_com = _libgmp.__gmpz_com
_MPZ_abs = _libgmp.__gmpz_abs
_MPZ_neg = _libgmp.__gmpz_neg
_MPZ_cmp = _libgmp.__gmpz_cmp
_MPZ_set = _libgmp.__gmpz_set
_MPZ_set_str = _libgmp.__gmpz_set_str
_MPZ_get_str = _libgmp.__gmpz_get_str
_MPZ_gcd = _libgmp.__gmpz_gcd
_MPZ_lcm = _libgmp.__gmpz_lcm
_MPZ_gcdext = _libgmp.__gmpz_gcdext
_MPZ_fac = _libgmp.__gmpz_fac_ui
_MPZ_powm = _libgmp.__gmpz_powm
_MPZ_pow_ui = _libgmp.__gmpz_pow_ui

# Gnu MP rational number routines
_MPQ_init = _libgmp.__gmpq_init
_MPQ_clear = _libgmp.__gmpq_clear
_MPQ_add = _libgmp.__gmpq_add
_MPQ_sub = _libgmp.__gmpq_sub
_MPQ_mul = _libgmp.__gmpq_mul
_MPQ_div = _libgmp.__gmpq_div
_MPQ_abs = _libgmp.__gmpq_abs
_MPQ_neg = _libgmp.__gmpq_neg
_MPQ_cmp = _libgmp.__gmpq_cmp
_MPQ_set = _libgmp.__gmpq_set
_MPQ_set_str = _libgmp.__gmpq_set_str
_MPQ_get_str = _libgmp.__gmpq_get_str
_MPQ_get_num = _libgmp.__gmpq_get_num
_MPQ_get_den = _libgmp.__gmpq_get_den


#
# Wrappers around GNU GMP mpz/mpq
# -------------------------------

class mpz(numbers.Integral):
    """Wrapper for GNU GMP integers."""

    def __init__(self, n=0):
        """Initialize self."""
        self._mpz = _c_mpz_struct()
        self._mpzp = ctypes.byref(self._mpz)
        _MPZ_init(self)
        if isinstance(n, mpz):
            _MPZ_set(self, n)
        elif isinstance(n, numbers.Integral):
            _MPZ_set_str(self, bytes(str(int(n)), 'ascii'), 10)
        else:
            raise TypeError("non-int")

    def __del__(self):
        _MPZ_clear(self)

    @property
    def numerator(self):
        return mpz(self)

    @property
    def denominator(self):
        return mpz(1)

    @property
    def _as_parameter_(self):
        return self._mpzp

    @staticmethod
    def from_param(arg):
        assert isinstance(arg, mpz)
        return arg

    def __apply_ret(self, func, ret, op1, op2):
        assert isinstance(ret, mpz)
        if not isinstance(op1, mpz):
            op1 = mpz(op1)
        if not isinstance(op2, mpz):
            op2 = mpz(op2)
        func(ret, op1, op2)
        return ret

    def __apply_ret_2_0(self, func, ret, op1):
        assert isinstance(ret, mpz)
        assert isinstance(op1, mpz)
        func(ret, op1)
        return ret

    def __apply_ret_2_1(self, func, op1, op2):
        if not isinstance(op1, mpz):
            op1 = mpz(op1)
        if not isinstance(op2, mpz):
            op2 = mpz(op2)
        return func(op1, op2)

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._set_hash()
        return self._hash

    def _set_hash(self):
        self._int = int(str(_MPZ_get_str(None, 10, self), 'ascii'))
        self._hash = hash(self._int)

    def __str__(self):
        if not hasattr(self, '_hash'):
            self._set_hash()
        return str(self._int)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.__apply_ret_2_1(_MPZ_cmp, self, other) < 0

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        return self.__apply_ret_2_1(_MPZ_cmp, self, other) == 0

    def __gt__(self, other):
        return self.__apply_ret_2_1(_MPZ_cmp, self, other) > 0

    def __ge__(self, other):
        return self > other or self == other

    def __add__(self, other):
        return self.__apply_ret(_MPZ_add, mpz(), self, other)

    def __radd__(self, other):
        return self.__apply_ret(_MPZ_add, mpz(), other, self)

    def __sub__(self, other):
        return self.__apply_ret(_MPZ_sub, mpz(), self, other)

    def __rsub__(self, other):
        return self.__apply_ret(_MPZ_sub, mpz(), other, self)

    def __mul__(self, other):
        try:
            return self.__apply_ret(_MPZ_mul, mpz(), self, other)
        except TypeError:
            if isinstance(other, float):
                return int(self) * other
            raise

    def __rmul__(self, other):
        return self.__apply_ret(_MPZ_mul, mpz(), other, self)

    def __truediv__(self, other):
        return int(self).__truediv__(int(other))

    def __rtruediv__(self, other):
        return int(other).__truediv__(int(self))

    def __floordiv__(self, other):
        return self.__apply_ret(_MPZ_div, mpz(), self, other)

    def __rfloordiv__(self, other):
        return self.__apply_ret(_MPZ_div, mpz(), other, self)

    def __and__(self, other):
        return self.__apply_ret(_MPZ_and, mpz(), self, other)

    def __rand__(self, other):
        return self.__apply_ret(_MPZ_and, mpz(), other, self)

    def __lshift__(self, other):
        raise NotImplementedError

    def __rlshift__(self, other):
        raise NotImplementedError

    def __rshift__(self, other):
        return int(self).__rshift__(int(other))

    def __rrshift__(self, other):
        raise NotImplementedError

    def __mod__(self, other):
        return self.__apply_ret(_MPZ_mod, mpz(), self, other)

    def __rmod__(self, other):
        return self.__apply_ret(_MPZ_mod, mpz(), other, self)

    def __xor__(self, other):
        return self.__apply_ret(_MPZ_xor, mpz(), self, other)

    def __rxor__(self, other):
        return self.__apply_ret(_MPZ_xor, mpz(), other, self)

    def __or__(self, other):
        return self.__apply_ret(_MPZ_ior, mpz(), self, other)

    def __ror__(self, other):
        return self.__apply_ret(_MPZ_ior, mpz(), other, self)

    __iadd__ = __add__
    __isub__ = __sub__
    __imul__ = __mul__
    __imod__ = __mod__
    __iand__ = __and__
    __ixor__ = __xor__
    __ior__ = __or__

    def __abs__(self):
        return self.__apply_ret_2_0(_MPZ_abs, mpz(), self)

    def __pos__(self):
        return mpz(self)

    def __neg__(self):
        return self.__apply_ret_2_0(_MPZ_neg, mpz(), self)

    def __pow__(self, other, mod=None):
        if not isinstance(other, mpz):
            other = mpz(other)
        if mod is not None and not isinstance(mod, mpz):
            mod = mpz(mod)
        if other < 0:
            raise ValueError
        ret = mpz()
        if mod:
            _MPZ_powm(ret, self, other, mod)
        else:
            _MPZ_pow_ui(ret, self, int(other))
        return ret

    def __rpow__(self, other, mod=None):
        raise NotImplementedError

    def __invert__(self):
        return self.__apply_ret_2_0(_MPZ_com, mpz(), self)

    def __ceil__(self):
        return mpz(self)

    def __floor__(self):
        return mpz(self)

    def __int__(self):
        return int(str(self))

    def __round__(self):
        return mpz(self)

    def __trunc__(self):
        return mpz(self)


class mpq(numbers.Rational):
    """Wrapper for GNU GMP rationals."""

    def __init__(self, p=0, q=1):
        """Initialize self."""
        self._mpq = _c_mpq_struct()
        self._mpqp = ctypes.byref(self._mpq)
        _MPQ_init(self)
        if q == 1 and isinstance(p, mpq):
            _MPQ_set(self, p)
        elif all(isinstance(_, numbers.Integral) for _ in (p, q)):
            _MPQ_set_str(self, bytes(str(p) + "/" + str(q), 'ascii'), 10)
        elif all(isinstance(_, numbers.Rational) for _ in (p, q)):
            e = p / q
            p, q = e.numerator, e.denominator
            _MPQ_set_str(self, bytes(str(p) + "/" + str(q), 'ascii'), 10)
        else:
            raise TypeError("non-rational")

    def __del__(self):
        _MPQ_clear(self)

    @property
    def numerator(self):
        ret = mpz()
        _MPQ_get_num(ret, self)
        return ret

    @property
    def denominator(self):
        ret = mpz()
        _MPQ_get_den(ret, self)
        return ret

    @property
    def _as_parameter_(self):
        return self._mpqp

    @staticmethod
    def from_param(arg):
        assert isinstance(arg, mpq)
        return arg

    def __apply_ret(self, func, ret, op1, op2):
        assert isinstance(ret, mpq)
        if not isinstance(op1, mpq):
            op1 = mpq(op1)
        if not isinstance(op2, mpq):
            op2 = mpq(op2)
        func(ret, op1, op2)
        return ret

    def __apply_ret_2_0(self, func, ret, op1):
        assert isinstance(ret, mpq)
        assert isinstance(op1, mpq)
        func(ret, op1)
        return ret

    def __apply_ret_2_1(self, func, op1, op2):
        if not isinstance(op1, mpq):
            op1 = mpq(op1)
        if not isinstance(op2, mpq):
            op2 = mpq(op2)
        return func(op1, op2)

    def __str__(self):
        return str(_MPQ_get_str(None, 10, self), 'ascii')

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.numerator, self.denominator))

    def __lt__(self, other):
        return self.__apply_ret_2_1(_MPQ_cmp, self, other) < 0

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        return self.__apply_ret_2_1(_MPQ_cmp, self, other) == 0

    def __gt__(self, other):
        return self.__apply_ret_2_1(_MPQ_cmp, self, other) > 0

    def __ge__(self, other):
        return self > other or self == other

    def __add__(self, other):
        return self.__apply_ret(_MPQ_add, mpq(), self, other)

    def __radd__(self, other):
        return self.__apply_ret(_MPQ_add, mpq(), other, self)

    def __sub__(self, other):
        return self.__apply_ret(_MPQ_sub, mpq(), self, other)

    def __mul__(self, other):
        return self.__apply_ret(_MPQ_mul, mpq(), self, other)

    def __rmul__(self, other):
        return self.__apply_ret(_MPQ_mul, mpq(), other, self)

    def __truediv__(self, other):
        return self.__apply_ret(_MPQ_div, mpq(), self, other)

    def __rtruediv__(self, other):
        return self.__apply_ret(_MPQ_div, mpq(), other, self)

    def __floordiv__(self, other):
        return mpz(int(self / other))

    def __rfloordiv__(self, other):
        raise NotImplementedError

    def __mod__(self, other):
        raise NotImplementedError

    def __rmod__(self, other):
        raise NotImplementedError

    def __iadd__(self, other):
        return self.__apply_ret(_MPQ_add, self, self, other)

    def __isub__(self, other):
        return self.__apply_ret(_MPQ_sub, self, self, other)

    def __imul__(self, other):
        return self.__apply_ret(_MPQ_mul, self, self, other)

    def __abs__(self):
        return self.__apply_ret_2_0(_MPQ_abs, mpq(), self)

    def __pos__(self):
        return mpq(self)

    def __neg__(self):
        return self.__apply_ret_2_0(_MPQ_neg, mpq(), self)

    def __pow__(self, other, mod=None):
        other = mpq(other)
        if mod is None and all(_.denominator == 1 for _ in (self, other)):
            if other.numerator >= 0:
                return self.numerator**other.numerator
            else:
                return mpq(1) / self.numerator**(-other.numerator)
        return NotImplemented

    def __rpow__(self, other, mod=None):
        raise NotImplementedError

    def __ceil__(self):
        raise NotImplementedError

    def __floor__(self):
        raise NotImplementedError

    def __int__(self):
        return int(self.numerator // self.denominator)

    def __round__(self):
        raise NotImplementedError

    def __trunc__(self):
        raise NotImplementedError


#
# Argument/return-type specs for Gnu MP routines
# ----------------------------------------------

# Gnu MP integer routines
_MPZ_init.argtypes = mpz,
_MPZ_clear.argtypes = mpz,
_MPZ_add.argtypes = mpz, mpz, mpz
_MPZ_sub.argtypes = mpz, mpz, mpz
_MPZ_mul.argtypes = mpz, mpz, mpz
_MPZ_mod.argtypes = mpz, mpz, mpz
_MPZ_and.argtypes = mpz, mpz, mpz
_MPZ_ior.argtypes = mpz, mpz, mpz
_MPZ_xor.argtypes = mpz, mpz, mpz
_MPZ_com.argtypes = mpz, mpz
_MPZ_abs.argtypes = mpz, mpz
_MPZ_neg.argtypes = mpz, mpz
_MPZ_cmp.argtypes = mpz, mpz
_MPZ_set.argtypes = mpz, mpz
_MPZ_set_str.argtypes = mpz, ctypes.c_char_p, ctypes.c_int
_MPZ_get_str.argtypes = ctypes.c_char_p, ctypes.c_int, mpz
_MPZ_gcd.argtypes = mpz, mpz, mpz
_MPZ_lcm.argtypes = mpz, mpz, mpz
_MPZ_gcdext.argtypes = mpz, mpz, mpz, mpz, mpz
_MPZ_fac.argtypes = mpz, ctypes.c_uint
_MPZ_powm.argtypes = mpz, mpz, mpz, mpz
_MPZ_pow_ui.argtypes = mpz, mpz, ctypes.c_uint

# non-default (int) return types
_MPZ_get_str.restype = ctypes.c_char_p

# Gnu MP rational number routines
_MPQ_init.argtypes = mpq,
_MPQ_clear.argtypes = mpq,
_MPQ_add.argtypes = mpq, mpq, mpq
_MPQ_sub.argtypes = mpq, mpq, mpq
_MPQ_mul.argtypes = mpq, mpq, mpq
_MPQ_abs.argtypes = mpq, mpq
_MPQ_neg.argtypes = mpq, mpq
_MPQ_cmp.argtypes = mpq, mpq
_MPQ_set.argtypes = mpq, mpq
_MPQ_set_str.argtypes = mpq, ctypes.c_char_p, ctypes.c_int
_MPQ_get_str.argtypes = ctypes.c_char_p, ctypes.c_int, mpq
_MPQ_get_num.argtypes = mpz, mpq
_MPQ_get_den.argtypes = mpz, mpq
# non-default (int) return types
_MPQ_get_str.restype = ctypes.c_char_p


def gcd(x, y):
    ret = mpz()
    _MPZ_gcd(ret, x, y)
    return ret


def gcdext(x, y):
    g, s, t = mpz(), mpz(), mpz()
    _MPZ_gcdext(g, s, t, x, y)
    return g, s, t


def lcm(x, y):
    ret = mpz()
    _MPZ_lcm(ret, x, y)
    return ret


def fac(x):
    ret = mpz()
    _MPZ_fac(ret, int(x))
    return ret
