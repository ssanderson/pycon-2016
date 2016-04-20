from freeze_globals import update_code


def foo(a, b, c, d, e, f, g, h, i):
    if a:
        if b:
            if c:
                return (a, b, c, d, e, f, g, h, i)

foo = update_code(foo, co_stacksize=1)

if __name__ == '__main__':
    for i in range(10000):
        print(*range(1, 10))
