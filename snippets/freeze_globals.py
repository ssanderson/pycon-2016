import struct
from types import CodeType, FunctionType


LOAD_CONST_OPCODE = 100
LOAD_GLOBAL_OPCODE = 116


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


def freeze_globals(f):
    """
    Decorator that replaces all the LOAD_GLOBAL instructions in a function with
    LOAD_CONST instructions.
    """
    code = f.__code__
    globals_ = f.__globals__
    orig_consts = code.co_consts
    names = code.co_names

    opcodes = list(code.co_code)

    i = 0
    new_consts = []
    while i < len(opcodes):
        opcode = opcodes[i]
        if opcode == LOAD_GLOBAL_OPCODE:
            # Unpack the next two bytes into a little-endian unsigned short.
            arg = struct.unpack("<H", bytes(opcodes[i + 1:i + 3]))

            # The argument to LOAD_GLOBAL is an index into co_names.
            name = names[arg[0]]

            # The content of co_names is the name of the global to look up.
            value = globals_[name]

            print("Freezing global %r with value %s." % (name, value))

            # Pack the index of the value in our new consts.
            packed_arg = struct.pack("<H", len(orig_consts) + len(new_consts))

            # Add the frozen value as a new constant.
            new_consts.append(value)

            # Replace the LOAD_GLOBAL with a LOAD_CONST of the location in the
            # new constants tuple.
            opcodes[i] = LOAD_CONST_OPCODE
            opcodes[i + 1] = packed_arg[0]
            opcodes[i + 2] = packed_arg[1]

            # Skip next two opcodes.
            i += 2
        else:
            i += 1

    new_consts = orig_consts + tuple(new_consts)
    new_bytecode = bytes(opcodes)

    return update_code(f, co_consts=new_consts, co_code=new_bytecode)


if __name__ == '__main__':

    x = 1
    y = 2

    @freeze_globals
    def foo():
        return x, y

    print("x=%s, y=%s" % foo())

    x = 3
    y = 4
    print("x=%s, y=%s" % foo())
