from types import CodeType, FunctionType


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


BINARY_ADD_OPCODE = 23
BINARY_MULTIPLY_OPCODE = 20


def add_to_mul(f):
    """
    Decorator that converts addition to multiplication.
    """
    instructions = list(f.__code__.co_code)
    new_instructions = []
    for instr in instructions:
        if instr == BINARY_ADD_OPCODE:
            new_instructions.append(BINARY_MULTIPLY_OPCODE)
        else:
            new_instructions.append(instr)
    return update_code(f, co_code=bytes(new_instructions))
