"""
Customization hack for broadcasting operations in SymPy Eq objects to lhs and rhs.
Latest source file is at: https://github.com/mathcube7/customize-sympy/
Blog post: https://awstip.com/customizing-pythons-sympy-for-easy-equation-manipulation-ca30b9d0dabf

### Usage

Apply arithmetic operations to sympy Eq objects:

    >>> eqn1 = Eq(x**2 - 4, 45)
    >>> eqn2 = eqn1 + 4  # __rmul__ is called; it applies +4 to both lhs and rhs
    >>> print(eqn2)
    Eq(x**2, 49)

Apply any sympy functions:

    >>> sqrt(eqn2)
    Eq(sqrt(x**2), 7)    # function `sqrt` will be applied to both lhs and rhs

Solve an equation:

    >>> solve(eqn1)      # equation is rewritten as an expression equal to zero
    [-7, 7]
    >>> nsolve(eqn1, -1), nsolve(eqn1, 1)
    (-7.0, 7.0)

"""

import sys
import types

import sympy


class Eq(sympy.Eq):

    def __add__(self, other):
        if isinstance(other, Eq):
            return Eq(self.lhs + other.lhs, self.rhs + other.rhs)
        return Eq(self.lhs + other, self.rhs + other)

    def __radd__(self, other):
        return Eq(self.lhs + other, self.rhs + other)

    def __sub__(self, other):
        if isinstance(other, Eq):
            return Eq(self.lhs - other.lhs, self.rhs - other.rhs)
        return Eq(self.lhs - other, self.rhs - other)

    def __rsub__(self, other):
        return Eq(self.lhs - other, self.rhs - other)

    def __mul__(self, other):
        if isinstance(other, Eq):
            return Eq(self.lhs * other.lhs, self.rhs * other.rhs)
        return Eq(self.lhs * other, self.rhs * other)

    def __rmul__(self, other):
        return Eq(other * self.lhs, other * self.rhs)

    def __truediv__(self, other):
        if isinstance(other, Eq):
            return Eq(self.lhs / other.lhs, self.rhs / other.rhs)
        return Eq(self.lhs / other, self.rhs / other)

    def __rtruediv__(self, other):
        return Eq(other / self.lhs, other / self.rhs)

    def __pow__(self, power, modulo=None):
        return Eq(self.lhs**power, self.rhs**power)


def _wrap_function(func):
    def f(*args, **kwargs):
        """
        Patch sympy function so it handles ``Eq`` as first argument correclty
        by broadcasting the `func` action to both ``eq.lhs`` and ``eq.rhs``.
        Functions `solve`, `nsolve`, etc. are handled differently, convering the
        equation object into an expression equal to zero: ``eq.lhs - eq.rhs``,
        which is the expected input for "solve" functions in SymPy.
        """
        if not args:
            return func(*args, **kwargs)
        if isinstance(args[0], Eq):
            eq = args[0]
            other_args = args[1:]
            if func.__name__ in ['solve', 'nsolve', 'dsolve']:
                return func(eq.lhs - eq.rhs, *other_args, **kwargs)
            else:
                return Eq(func(eq.lhs, *other_args, **kwargs),
                          func(eq.rhs, *other_args, **kwargs))
        else:
            return func(*args, **kwargs)

    return f

names = dir(sympy)
names = [name for name in names if name[0] in 'abcdefghijklmnopqrstuvwxyz']
this_module = sys.modules[__name__]

for name in names:
    func = getattr(sympy, name)
    if (isinstance(func, types.FunctionType)
            or isinstance(func, sympy.FunctionClass)):
        setattr(this_module, name, _wrap_function(func))
