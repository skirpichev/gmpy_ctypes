"""Basic tests for gmpy_ctypes."""

import math

import hypothesis

from gmpy_ctypes import mpz


@hypothesis.given(x=hypothesis.strategies.integers(-1000, 1000),
                  y=hypothesis.strategies.integers(-1000, 1000))
@hypothesis.settings(deadline=None)
@hypothesis.example(x=42, y=0)
def test_mpz(x, y):
    mx, my = mpz(x), mpz(y)

    assert mx.numerator == x.numerator
    assert mx.denominator == x.denominator

    assert str(y) == str(my)
    assert hash(x) == hash(mx)
    assert str(x) == str(mx)
    assert repr(x) == repr(mx)

    assert mx + my == x + my == mx + y == x + y
    assert mx - my == x - my == mx - y == x - y
    assert mx * my == x * my == mx * y == x * y
    if y != 0:
        assert mx % my == x % my == mx % y == x % y
        assert mx // my == x // my == mx // y == x // y
    assert mx & my == x & my == mx & y == x & y
    assert mx | my == x | my == mx | y == x | y
    assert mx ^ my == x ^ my == mx ^ y == x ^ y
    assert +mx == x
    assert -mx == -x
    assert (mx == my) == (x == my) == (mx == y) == (x == y)
    assert (mx != my) == (x != my) == (mx != y) == (x != y)
    assert (mx >= my) == (x >= y)
    assert (mx <= my) == (x <= y)
    assert (mx > my) == (x > my) == (mx > y) == (x > y)
    assert (mx < my) == (x < my) == (mx < y) == (x < y)
    assert ~mx == ~x
    assert int(mx) == int(x)
    assert abs(mx) == abs(x)
    assert round(mx) == round(x)
    assert math.floor(mx) == math.floor(x)
    assert math.ceil(mx) == math.ceil(x)
    assert math.trunc(mx) == math.trunc(x)

    x += y
    mx += my
    assert x == mx

    x -= y
    mx -= y
    assert x == mx

    x *= y
    mx *= my
    assert x == mx

    if y != 0:
        x %= y
        mx %= my
        assert x == mx

    x &= y
    mx &= my
    assert x == mx

    x |= y
    mx |= my
    assert x == mx

    x ^= y
    mx ^= my
    assert x == mx
