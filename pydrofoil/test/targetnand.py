import os
from rpython.rlib import rarithmetic
from pydrofoil.test.supportcode import load_rom
from pydrofoil.makecode import *

nandir = os.path.join(os.path.dirname(__file__), "c.ir")
outnandpy = os.path.join(os.path.dirname(__file__), "out.py")

def make_code():
    print "making rpython code"
    with open(nandir, "rb") as f:
        s = f.read()
    res = parse_and_make_code(s, "supportcode")
    with open(outnandpy, "w") as f:
        f.write(res)
    from pydrofoil.test import out, supportcode
    return out, supportcode

def target(*args):
    make_code()
    return main

def main(argv):
    from pydrofoil.test.out import func_zmymain
    if len(argv) != 4:
        print "usage: %s <binary> <maxcycle> <debug>" % (argv[0], )
        return -1
    load_rom(argv[1])
    func_zmymain(rarithmetic.r_uint(int(argv[2])), int(argv[3]))
    return 0


if __name__ == '__main__':
    import sys
    try:
        target()(sys.argv)
    except:
        import pdb;pdb.xpm()
        raise
