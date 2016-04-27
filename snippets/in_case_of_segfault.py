import dis
from functools import partial
from types import CodeType, FunctionType


def update(f, **kwargs):
    "A function that performs a functional update on a function."
    code = f.__code__
    attrs = [
        'co_argcount', 'co_kwonlyargcount', 'co_nlocals', 'co_stacksize',
        'co_flags', 'co_code', 'co_consts', 'co_names', 'co_varnames',
        'co_filename', 'co_name', 'co_firstlineno', 'co_lnotab',
        'co_freevars', 'co_cellvars',
    ]
    newcode = CodeType(*(kwargs.get(a, getattr(code, a)) for a in attrs))
    return FunctionType(
        newcode, f.__globals__, f.__name__, f.__defaults__, f.__closure__,
    )

my_code = CodeType(1,
                   0,
                   1,
                   2,
                   67,
                   bytes([124, 0, 0, 100, 0, 0, 23, 83]),
                   (1,),
                   (),
                   ('x',),
                   '<string>',
                   'addone',
                   42,
                   b"",
                   (),
                   ())


my_addone = FunctionType(my_code, {})


def addone(x):
    return x + 1


def addtwo(x):
    return x + 2


def break_glass():
    import sys
    sys._getframe(1).f_globals.update(globals())
