How Does Python Execute Anything?
---------------------------------
(3 minutes)

In this section, we provide an introduction to the `code` type.  In particular,
we draw attention to it's `co_code` attribute, which contains the actual
instructions executed by the interpreter.

- Write a simple function in the REPL.
- Call it.
- What actually happened there?
- Show the `__code__` attribute.
- Show the `co_code`.
- What the heck does is this inscrutable bytestring?

Intro to Bytecode
-----------------
(7 minutes)

In this section we walk through a sequence of simple Python functions, showing
the disassembly of each and walking through the state of the CPython Virtual
machine as it executes the instructions.  The important ideas here are that
CPython is a stack-based virtual machine, that you can use the `dis` module to
inspect bytecode, and that there are many different kinds of instructions.
Important classes of instructions are `LOAD`s, `STORE`s, `JUMP`s, and `BINARY`
operators.

**First Example:**

Should teach the audience what the stack is, showing that values get pushed
onto and popped from the stack.

Source:

    def add(a, b):
        a + b

Disassembly:


    3           0 LOAD_FAST                0 (a)
                3 LOAD_FAST                1 (b)
                6 BINARY_ADD
                7 RETURN_VALUE

**Second Example:**

Should teach the audience what a store looks like.

Source:

    def add_with_store(a, b):
        x = a + b
        return x

Disassembly:

    3           0 LOAD_FAST                0 (a)
                3 LOAD_FAST                1 (b)
                6 BINARY_ADD
                7 STORE_FAST               2 (x)

    4          10 LOAD_FAST                2 (x)
               13 RETURN_VALUE

**Third Example:**

Should teach the audience what a jump looks like, and introduces the
distinction between variables and constants.  This is foreshadowing two of the
important problems we'll be solving later: managing addition of new values to
the `co_consts`, and the ensuring correct resolution of jumps.

Source:

    def abs(x):
        if x > 0:
            return x
        else:
            return -x

Disassembly:

    3           0 LOAD_FAST                0 (x)
                3 LOAD_CONST               1 (0)
                6 COMPARE_OP               4 (>)
                9 POP_JUMP_IF_FALSE       16

    4          12 LOAD_FAST                0 (x)
               15 RETURN_VALUE

    6     >>   16 LOAD_FAST                0 (x)
               19 UNARY_NEGATIVE
               20 RETURN_VALUE
               21 LOAD_CONST               0 (None)
               24 RETURN_VALUE

Building a Code Object From Scratch
-----------------------------------
(10 minutes)

Python functions are objects just like anything else in Python.  This means
they must be instances of some type.  What would it take to build a function
object from "scratch"?

Let's make a simple function equivalent to:

    def addone(x):
        return x + 1

What do we need to pass to CodeType?

    In [1]: from types import CodeType

    In [2]: CodeType?
    Docstring:
    code(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
          constants, names, varnames, filename, name, firstlineno,
          lnotab[, freevars[, cellvars]])

    Create a code object.  Not for the faint of heart.
    Type:      type

The disassembly for our desired function:

    3           0 LOAD_FAST                0 (x)
                3 LOAD_CONST               1 (1)
                6 BINARY_ADD
                7 RETURN_VALUE

The bytecode:

    >>> addone.__code__.co_code
    b'|\x00\x00d\x01\x00\x17S'

This is easier to read interpreting the bytes as ints:

    >>> list(addone.__code__.co_code)
    [124, 0, 0, 100, 1, 0, 23, 83]

Each instruction is a single unsigned byte.  For instructions that take
arguments, two bytes are used for the argument.

- `124` is the opcode for `LOAD_FAST`.  The next two values are two bytes
  representing the argument to `LOAD_FAST`, which is the index into the fast
  (aka local) variable storage, interpreted as a little-endian 2-byte integer.

- `100` is the opcode for `LOAD_CONST`.  The argument to `LOAD_CONST` is also a
  2-byte little-endian (note that the `1` comes first!) integer, representing
  the index into the constants tuple of the constant to load.

- `23` is the opcode for `BINARY_ADD`.  `BINARY_ADD` is always the same, so
  there's no argument at the bytecode level.

- `83` is the opcode for `RETURN_VALUE`.  Like `BINARY_ADD` it just operates on
  the stack, so it doesn't take a bytecode argument.

That covers the bytecode.  What are the other arguments we need?

- `argcount` is the number of arguments accepted by the function. `1` for us.
- `kwonlyargcount` is 0 because we have no keyword only arguments. `0` for us.
- `nlocals` is the number of local variables. `1` for us.
- `stacksize` is the maximum number of values that will be on the stack at any
  given time.  In our case, the maximum value is 2, right before we execute
  `BINARY_ADD`.
- `flags` is a 32-bit bitmask providing metadata about the function.  There are
  lots of flags:

        # Are we optimized?  Always True for functions.
        CO_OPTIMIZED = 0x0001

        # Do we create a new locals?  Always True for functions.
        CO_NEWLOCALS = 0x0002

        # Do we accept *args?
        CO_VARARGS = 0x0004

        # Do we acept **kwargs?
        CO_VARKEYWORDS = 0x0008

        # Is this function defined inside another function?
        CO_NESTED = 0x0010

        # Is this function a generator?
        CO_GENERATOR = 0x0020

        # The CO_NOFREE flag is set if there are no free or cell variables.
        # This information is redundant, but it allows a single flag test
        # to determine whether there is any extra work to be done when the
        # call frame is setup.
        CO_NOFREE = 0x0040

        # The CO_COROUTINE flag is set for coroutines creates with the
        # types.coroutine decorator. This converts old-style coroutines into
        # python3.5 style coroutines.
        CO_COROUTINE = 0x0080
        CO_ITERABLE_COROUTINE = 0x0100

        # __future__ import flags.
        CO_FUTURE_DIVISION = 0x2000
        CO_FUTURE_ABSOLUTE_IMPORT = 0x4000  # Do absolute imports by default.
        CO_FUTURE_WITH_STATEMENT = 0x8000
        CO_FUTURE_PRINT_FUNCTION = 0x10000
        CO_FUTURE_UNICODE_LITERALS = 0x20000

        CO_FUTURE_BARRY_AS_BDFL = 0x40000  # Old April Fool's joke.
        CO_FUTURE_GENERATOR_STOP = 0x80000

    in our case, we want to set `CO_OPTIMIZED`, and `CO_NEWLOCALS`, and
    `CO_NOFREE`, so `flags` should be `0x0001 | 0x0002 | 0x0040 = 0x0043 = 67`.
- `codestring` is the bytecode string we just built.
- `constants` is the constants tuple.  A standard function always has `None` as
  constant 0.  Our only other constant is the integer literal `1`, so the
  constants should be `(None, 1)`.
- `names` should be the names of global variables and names of attributes
  accessed.  We don't have any.
- `varnames` is a tuple of local variable names.  We should have `('x',)`.
- `filename` is whatever we want.  We'll use `'pycon2016.py'`.
- `name` is `'addone'`.
- `firstlineno` is whatever we want. We'll use `1`.
- `lnotab` is the binary format representing a mapping from instruction index
  to line number increment.
- `freevars` is a tuple containing names of variables that we're closing over.
  In this case it's just `()`.
- `cellvars` is a tuple containing names of variables that are closed over by
  functions defined inside of our function.  It's also just `()` here.

Putting them all together we have this:

    # This sadly doesn't accept keyword arguments.
    code = CodeType(
        1,                                     # argcount
        0,                                     # kwonlyargcount
        1,                                     # nlocals
        2,                                     # stacksize
        67,                                    # flags
        bytes([124, 0, 0, 100, 1, 0, 23, 83]), # codestring
        (None, 1),                             # constants
        (),                                    # names
        ('x',),                                # varnames
        'pycon2016.py',                        # filename
        'addone',                              # name
        1,                                     # firstlineno
        bytes([0, 1]),                         # lnotab
        (),                                    # freevars
        (),                                    # cellvars
    )

Huzzah! Let's verify that this worked:

    >>> dis.dis(code)
      2           0 LOAD_FAST                0 (x)
                  3 LOAD_CONST               1 (1)
                  6 BINARY_ADD
                  7 RETURN_VALUE

Building a Function Object from Code
------------------------------------
(2 minutes)

Now that we've got a `code` object, how do we turn that into a proper function?

    In [1]: from types import FunctionType

    In [2]: FunctionType?
    Docstring:
    function(code, globals[, name[, argdefs[, closure]]])

    Create a function object from a code object and a dictionary.
    The optional name string overrides the name from the code object.
    The optional argdefs tuple specifies the default argument values.
    The optional closure tuple supplies the bindings for free variables.
    Type:      type

This is, thankfully, much simpler than `CodeType`.

    In [6]: addone = FunctionType(code, globals())

    In [7]: addone(2)
    Out[7]: 3

Modifying Existing Code Objects
-------------------------------
(5 minutes)

It's not often that we want to construct a function (or module, or class) from
whole cloth. Python is already a pretty good language for generating bytecode.

What if we realized we actually wanted to add two instead of one?

    In [9]: addone.__code__.co_consts = (None, 2)
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    <ipython-input-9-b34300c5889a> in <module>()
    ----> 1 addone.__code__.co_consts = (None, 2)

    AttributeError: readonly attribute

Thankfully, `code` objects are immutable, so we can't just mutate the consts in
place.  What we can do, however, is take an existing code object, copy all of
its attributes except the ones we want to replace, and create a new code object.

    def update_code(f, **kwargs):
        """Update attributes of a function's __code__."""

        code = f.__code__
        newcode = CodeType(
            kwargs.get('co_argcount', code.co_argcount),
            kwargs.get('co_kwonlyargcount', code.co_kwonlyargcount),
            kwargs.get('co_nlocals', code.co_nlocals),
            kwargs.get('co_stacksize', code.co_stacksize),
            kwargs.get('co_flags', code.co_flags),
            kwargs.get('co_code', code.co_code),
            kwargs.get('co_consts', code.co_consts),
            kwargs.get('co_names', code.co_names),
            kwargs.get('co_varnames', code.co_varnames),
            kwargs.get('co_filename', code.co_filename),
            kwargs.get('co_name', code.co_name),
            kwargs.get('co_firstlineno', code.co_firstlineno),
            kwargs.get('co_lnotab', code.co_lnotab),
            kwargs.get('co_freevars', code.co_freevars),
            kwargs.get('co_cellvars', code.co_cellvars),
        )
        return FunctionType(
            newcode, f.__globals__, f.__name__, f.__defaults__, f.__closure__,
        )

    In [1]: addtwo = update_code(addone, co_consts=(None, 2))

    In [2]: addtwo(1)
    Out[2]: 3

Updating the Bytecode
---------------------
