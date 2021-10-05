from numba import jit, njit, prange
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print((te-ts)*1000, 'ms')
        return result
    return timed

# @timeit
# @njit()
# def rng(a):
#     b = 0
#     for i in range(a):
#         b = b**i
#     return b

# rng(10000000)
