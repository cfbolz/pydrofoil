from rpython.rlib.nonconst import NonConstant
from rpython.rlib.objectmodel import we_are_translated, always_inline
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib import jit
from rpython.rlib import rmmap
from rpython.rtyper.lltypesystem import rffi, lltype

class MemBase(object):
    def close(self):
        pass

    def is_aligned(self, addr, num_bytes):
        if num_bytes == 1:
            return True
        elif num_bytes == 2:
            return addr & 0b1 == 0
        elif num_bytes == 4:
            return addr & 0b11 == 0
        elif num_bytes == 8:
            return addr & 0b111 == 0
        else:
            assert 0, "invalid num_bytes"

    def read(self, start_addr, num_bytes):
        if not self.is_aligned(start_addr, num_bytes):
            # not aligned! slow path
            return self._unaligned_read(start_addr, num_bytes)
        return self._aligned_read(start_addr, num_bytes)

    def _aligned_read(self, start_addr, num_bytes):
        raise NotImplementedError

    @jit.unroll_safe
    def _unaligned_read(self, start_addr, num_bytes):
        value = r_uint(0)
        for i in range(num_bytes - 1, -1, -1):
            value = value << 8
            value = value | self._aligned_read(start_addr + i, 1)
        return value

    def write(self, start_addr, num_bytes, value):
        if not self.is_aligned(start_addr, num_bytes):
            # not aligned! slow path
            return self._unaligned_write(start_addr, num_bytes, value)
        return self._aligned_write(start_addr, num_bytes, value)

    def _aligned_write(self, start_addr, num_bytes, value):
        raise NotImplementedError

    @jit.unroll_safe
    def _unaligned_write(self, start_addr, num_bytes, value):
        for i in range(num_bytes):
            self._aligned_write(start_addr + i, 1, value & 0xff)
            value = value >> 8
        assert not value

class MmapMemory(MemBase):
    SIZE = 8 * 1024 * 1024 * 1024 # 8 GB should be fine

    def __init__(self):
        if we_are_translated():
            nc = NonConstant
        else:
            nc = lambda x: x
        mem = rmmap.c_mmap(
            nc(rmmap.NULL),
            nc(self.SIZE),
            nc(rmmap.PROT_READ | rmmap.PROT_WRITE),
            nc(rmmap.MAP_PRIVATE | rmmap.MAP_ANONYMOUS),
            nc(-1), nc(0))
        mem = rffi.cast(rffi.UNSIGNEDP, mem)
        self.mem = mem

    def close(self):
        if we_are_translated():
            nc = NonConstant
        else:
            nc = lambda x: x
        rmmap.c_munmap_safe(rffi.cast(rffi.CCHARP, self.mem), nc(self.SIZE))
        self.mem = lltype.nullptr(rffi.UNSIGNEDP.TO)

    @always_inline
    def _split_addr(self, start_addr, num_bytes):
        mem_offset = start_addr >> 3
        inword_addr = start_addr & 0b111
        # little endian
        if num_bytes == 8:
            mask = r_uint(-1)
        else:
            mask = (r_uint(1) << (num_bytes * 8)) - 1
        return mem_offset, inword_addr, mask

    def _aligned_read(self, start_addr, num_bytes):
        mem_offset, inword_addr, mask = self._split_addr(start_addr, num_bytes)
        data = self.mem[mem_offset]
        if num_bytes == 8:
            assert inword_addr == 0
            return data
        return (data >> (inword_addr * 8)) & mask

    def _aligned_write(self, start_addr, num_bytes, value):
        mem_offset, inword_addr, mask = self._split_addr(start_addr, num_bytes)
        if num_bytes == 8:
            assert inword_addr == 0
            self.mem[mem_offset] = value
            return
        assert value & ~mask == 0
        olddata = self.mem[mem_offset]
        mask <<= inword_addr * 8
        value <<= inword_addr * 8
        self.mem[mem_offset] = (olddata & ~mask) | value


class BlockMemory(MemBase):
    ADDRESS_BITS_BLOCK = 20 # 1 MB
    BLOCK_SIZE = 2 ** ADDRESS_BITS_BLOCK
    BLOCK_MASK = BLOCK_SIZE - 1

    def __init__(self):
        self.blocks = {}
        self.last_block = None
        self.last_block_addr = r_uint(0)

    def get_block(self, block_addr):
        last_block = self.last_block
        if last_block is not None and block_addr == self.last_block_addr:
            block = last_block
        else:
            block = self._get_block(block_addr)
            self.last_block = block
            self.last_block_addr = block_addr
        return block

    @jit.elidable
    def _get_block(self, block_addr):
        if block_addr in self.blocks:
            return self.blocks[block_addr]
        res = self.blocks[block_addr] = [r_uint(0)] * (self.BLOCK_SIZE // 8)
        return res

    @always_inline
    def _split_addr(self, start_addr, num_bytes):
        block_addr = start_addr >> self.ADDRESS_BITS_BLOCK
        block = self.get_block(block_addr)
        start_addr = start_addr & self.BLOCK_MASK
        block_offset = start_addr >> 3
        inword_addr = start_addr & 0b111
        # little endian
        if num_bytes == 8:
            mask = r_uint(-1)
        else:
            mask = (r_uint(1) << (num_bytes * 8)) - 1
        return block, block_offset, inword_addr, mask

    def _aligned_read(self, start_addr, num_bytes):
        block, block_offset, inword_addr, mask = self._split_addr(start_addr, num_bytes)
        data = block[block_offset]
        if num_bytes == 8:
            assert inword_addr == 0
            return data
        return (data >> (inword_addr * 8)) & mask

    def _aligned_write(self, start_addr, num_bytes, value):
        block, block_offset, inword_addr, mask = self._split_addr(start_addr, num_bytes)
        if num_bytes == 8:
            assert inword_addr == 0
            block[block_offset] = value
            return
        assert value & ~mask == 0
        olddata = block[block_offset]
        mask <<= inword_addr * 8
        value <<= inword_addr * 8
        block[block_offset] = (olddata & ~mask) | value

