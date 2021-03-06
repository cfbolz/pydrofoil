import pytest
from pydrofoil.makecode import *

import os

thisdir = os.path.dirname(__file__)
cir = os.path.join(thisdir, "c.ir")
excir = os.path.join(thisdir, "exc.ir")
mipsir = os.path.join(thisdir, "mips.ir")
riscvir = os.path.join(thisdir, "riscv_model_RV64.ir")
outpy = os.path.join(thisdir, "out.py")
outmipspy = os.path.join(thisdir, "outmips.py")
outriscvpy = os.path.join(thisdir, "outriscv.py")

elfs = """
rv64ui-p-addi.elf rv64um-v-mul.elf rv64um-v-mulhu.elf rv64um-p-div.elf
rv64um-p-rem.elf rv64ua-v-amoadd_w.elf rv64ua-v-amomax_d.elf
"""

elfs = [os.path.join(thisdir, fn) for fn in elfs.split()]


addrom = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "nand2tetris", "input", "Add.hack.bin")
sumrom = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "nand2tetris", "input", "sum.hack.bin")

def test_enum():
    res = parse_and_make_code("""
enum zjump {
  zJDONT,
  zJGT,
  zJEQ,
  zJGE,
  zJLT,
  zJNE,
  zJLE,
  zJMP
}
""")
    assert """\
class Enum_zjump(object):
    zJDONT = 0
    zJGT = 1
    zJEQ = 2
    zJGE = 3
    zJLT = 4
    zJNE = 5
    zJLE = 6
    zJMP = 7
""" in res

def test_union():
    res = parse_and_make_code("""
union zinstr {
  zAINST: %bv16,
  zCINST: (%bv1, (%bool, %bool, %bool), %bool)
}
""")
    assert "class Union_zinstr(object):" in res
    assert "class Union_zinstr_zAINST(Union_zinstr):" in res
    assert "class Union_zinstr_zCINST(Union_zinstr):" in res

def test_exceptions(capsys):
    import py
    s = """
union zexception {
  zEpair: (%i64, %i64),
  zEstring: %string,
  zEunknown: %unit
}

val znot_bool = "not" : (%bool) ->  %bool

val zeq_int = "eq_int" : (%i, %i) ->  %bool

val zeq_bool = "eq_bool" : (%bool, %bool) ->  %bool

val zprint = "print_endline" : (%string) ->  %unit

val zprint_int = "print_int" : (%string, %i) ->  %unit

val zf : (%unit) ->  %unit

fn zf(zgsz30) {
  zgaz30_lz30 : %union zexception;
  zgaz30_lz30 = zEstring("test");
  current_exception = zgaz30_lz30;
  have_exception = true;
  throw_location = "fail_exception.sail 14:16 - 14:38";
  arbitrary;
}

val zg : (%unit) ->  %string

fn zg(zgsz31) {
  zgsz33_lz32 : %unit;
  zgsz33_lz32 = zprint("in g()");
  return = "g return";
  end;
}

val zmain : (%unit) ->  %unit

fn zmain(zgsz34) {
  zgsz39_lz320 : %unit;
  zgaz32_lz331 : %string;
  zgaz32_lz331 = zg(());
  jump have_exception goto 5 ` "unknown location";
  goto 6;
  goto 21;
  zgsz38_lz332 : %unit;
  zgsz38_lz332 = zprint(zgaz32_lz331);
  zgsz37_lz330 : %unit;
  zgsz37_lz330 = zf(());
  jump have_exception goto 12 ` "unknown location";
  goto 13;
  goto 21;
  zgaz33_lz327 : %union zexception;
  zgsz35_lz329 : (%i64, %i64);
  zgsz35_lz329.0 = 42;
  zgsz35_lz329.1 = 24;
  zgaz33_lz327 = zEpair(zgsz35_lz329);
  current_exception = zgaz33_lz327;
  have_exception = true;
  throw_location = "fail_exception.sail 30:4 - 30:24";
  jump @not(have_exception) goto 41 ` "fail_exception.sail 27:2 - 39:3";
  have_exception = false;
  jump current_exception is zEunknown goto 26 ` "fail_exception.sail 33:4 - 33:14";
  zgsz39_lz320 = zprint("Caught Eunknown");
  goto 41;
  jump current_exception is zEpair goto 33 ` "fail_exception.sail 34:4 - 34:15";
  zx_lz324 : %i64;
  zx_lz324 = current_exception as zEpair.ztup0;
  zy_lz325 : %i64;
  zy_lz325 = current_exception as zEpair.ztup1;
  zgsz39_lz320 = zprint("Caught Epair");
  goto 41;
  jump current_exception is zEstring goto 40 ` "fail_exception.sail 35:4 - 35:16";
  zstr_lz322 : %string;
  zstr_lz322 = current_exception as zEstring;
  zgsz312_lz323 : %unit;
  zgsz312_lz323 = zprint("Caught Estring");
  zgsz39_lz320 = zprint(zstr_lz322);
  goto 41;
  have_exception = true;
  zgsz338_lz321 : %unit;
  zgsz338_lz321 = zgsz39_lz320;
  zgsz314_lz318 : %unit;
  zgsz314_lz318 = ();
  jump @not(have_exception) goto 48 ` "fail_exception.sail 40:2 - 42:3";
  have_exception = false;
  zgsz314_lz318 = zprint("Unreachable!");
  zgsz337_lz319 : %unit;
  zgsz337_lz319 = zgsz314_lz318;
  zgsz317_lz311 : %unit;
  zgaz35_lz316 : %union zexception;
  zgsz316_lz317 : (%i64, %i64);
  zgsz316_lz317.0 = 33;
  zgsz316_lz317.1 = 1;
  zgaz35_lz316 = zEpair(zgsz316_lz317);
  current_exception = zgaz35_lz316;
  have_exception = true;
  throw_location = "fail_exception.sail 43:6 - 43:25";
  jump @not(have_exception) goto 70 ` "fail_exception.sail 43:2 - 49:3";
  have_exception = false;
  jump current_exception is zEpair goto 69 ` "fail_exception.sail 44:4 - 44:15";
  zx_lz313 : %i64;
  zx_lz313 = current_exception as zEpair.ztup0;
  zgsz318_lz315 : %unit;
  zgsz318_lz315 = zprint("2nd try Caught Epair");
  zgsz320_lz314 : %i = zx_lz313;
  zgsz317_lz311 = zprint_int("x = ", zgsz320_lz314);
  goto 70;
  zgsz317_lz311 = ();
  zgsz336_lz312 : %unit;
  zgsz336_lz312 = zgsz317_lz311;
  zgsz322_lz35 : %unit;
  zgaz36_lz310 : %union zexception;
  zgaz36_lz310 = zEunknown(());
  current_exception = zgaz36_lz310;
  have_exception = true;
  throw_location = "fail_exception.sail 50:6 - 50:23";
  jump @not(have_exception) goto 93 ` "fail_exception.sail 50:2 - 54:3";
  have_exception = false;
  zgsz325_lz37 : %unit;
  zgaz37_lz38 : %string;
  zgaz37_lz38 = zg(());
  jump have_exception goto 85 ` "unknown location";
  goto 86;
  goto 89;
  zgsz323_lz39 : %unit;
  zgsz323_lz39 = ();
  zgsz325_lz37 = zgsz323_lz39;
  jump @not(have_exception) goto 92 ` "fail_exception.sail 51:9 - 53:5";
  have_exception = false;
  zgsz325_lz37 = zprint("caught old exception");
  zgsz322_lz35 = zgsz325_lz37;
  zgsz335_lz36 : %unit;
  zgsz335_lz36 = zgsz322_lz35;
  zgsz330_lz31 : %unit;
  zgsz328_lz33 : %unit;
  zgaz38_lz34 : %union zexception;
  zgaz38_lz34 = zEunknown(());
  current_exception = zgaz38_lz34;
  have_exception = true;
  throw_location = "fail_exception.sail 56:8 - 56:24";
  jump @not(have_exception) goto 108 ` "fail_exception.sail 56:4 - 58:5";
  have_exception = false;
  jump current_exception is zEstring goto 107 ` "fail_exception.sail 57:6 - 57:16";
  zgsz328_lz33 = ();
  goto 108;
  have_exception = true;
  zgsz330_lz31 = zgsz328_lz33;
  jump @not(have_exception) goto 115 ` "fail_exception.sail 55:2 - 62:3";
  have_exception = false;
  jump current_exception is zEunknown goto 114 ` "fail_exception.sail 60:4 - 60:14";
  zgsz330_lz31 = zprint("Fall through OK");
  goto 115;
  zgsz330_lz31 = ();
  zgsz334_lz32 : %unit;
  zgsz334_lz32 = zgsz330_lz31;
  zgsz333_lz30 : %unit;
  zgsz333_lz30 = zf(());
  jump have_exception goto 121 ` "unknown location";
  goto 122;
  goto 124;
  return = ();
  end;
  arbitrary;
}
"""
    res = parse_and_make_code(s, "supportcode")
    d = {}
    res = py.code.Source(res)
    exec res.compile() in d
    d['func_zmain'](())
    out, err = capsys.readouterr()
    assert out == """\
in g()
g return
Caught Estring
test
2nd try Caught Epair
x = 33
in g()
Fall through OK
"""
    assert d['r'].have_exception

def test_exceptions2(capsys):
    import py
    with open(excir, "rb") as f:
        s = f.read()
    res = parse_and_make_code(s, "supportcode")
    res = py.code.Source(res)
    d = {}
    exec res.compile() in d
    d['func_zmain'](())
    out, err = capsys.readouterr()
    assert out == """\
i = 1
i = 2
i = 3
i = 3
i = 2
i = 1
j = 1
j = 2
j = 3
k = 0x01
k = 0x02
k = 0x03
Caught
Looping
Caught inner exception
Caught outer exception
Outer handler
Outer handler
Once
Once
ok
ok
R = 3
"""
    assert not d['r'].have_exception

def test_full_nand():
    import py
    from pydrofoil.test import supportcode
    from rpython.translator.interactive import Translation
    with open(cir, "rb") as f:
        s = f.read()
    res = parse_and_make_code(s, "supportcode")
    with open(outpy, "w") as f:
        f.write(res)

    # bit of a hack
    from pydrofoil.test import out
    supportcode.load_rom(addrom)
    zmymain = out.func_zmymain
    zmymain(10, True)
    assert out.r.zD == 5
    assert out.r.zA == 0
    assert out.r.zPC == 11
    supportcode.load_rom(sumrom)
    zmymain(2000, True)
    assert supportcode.my_read_mem(17) == 5050

    def main():
        supportcode.load_rom(addrom)
        zmymain(10, False)
    t = Translation(main, [])
    t.rtype() # check that it's rpython

@pytest.mark.xfail
def test_full_mips():
    import py
    with open(mipsir, "rb") as f:
        s = f.read()
    res = parse_and_make_code(s, "supportcode")
    with open(outmipspy, "w") as f:
        f.write(res)
    d = {}
    res = py.code.Source(res)
    exec res.compile() in d

@pytest.fixture(scope='session')
def riscvmain():
    from pydrofoil.test.targetriscv import make_code
    outriscv, supportcoderiscv = make_code()
    supportcoderiscv.g.config_print_instr = False
    supportcoderiscv.g.config_print_reg = False
    supportcoderiscv.g.config_print_mem_access = False
    supportcoderiscv.g.config_print_platform = False
    res = supportcoderiscv.get_main()
    res.supportcoderiscv = supportcoderiscv
    return res

@pytest.mark.parametrize("elf", elfs)
def test_full_riscv(riscvmain, elf):
    riscvmain(['executable', elf])

def test_load_dump(riscvmain):
    d = riscvmain.supportcoderiscv.parse_dump_file(os.path.join(thisdir, 'dhrystone.riscv.dump'))
    assert d[0x8000218a] == '.text: Proc_1 6100                	ld	s0,0(a0)'
