import numpy as np
from math import log2
# //////////////////
#
#       HELPERS
#
# ///////////////////

ZERO = np.uint64(0)
ONE = np.uint64(1)
TWO = np.uint64(2)

square = {
    1:'a8',                 2:'b8',                  4:'c8',                  8:'d8',                  16:'e8',                  32:'f8',                  64:'g8',                  128:'h8', 
    256:'a7',               512:'b7',                1024:'c7',               2048:'d7',               4096:'e7',                8192:'f7',                16384:'g7',               32768:'h7', 
    65536:'a6',             131072:'b6',             262144:'c6',             524288:'d6',             1048576:'e6',             2097152:'f6',             4194304:'g6',             8388608:'h6', 
    16777216:'a5',          33554432:'b5',           67108864:'c5',           134217728:'d5',          268435456:'e5',           536870912:'f5',           1073741824:'g5',          2147483648:'h5', 
    4294967296:'a4',        8589934592:'b4',         17179869184:'c4',        34359738368:'d4',        68719476736:'e4',         137438953472:'f4',        274877906944:'g4',        549755813888:'h4', 
    1099511627776:'a3',     2199023255552:'b3',      4398046511104:'c3',      8796093022208:'d3',      17592186044416:'e3',      35184372088832:'f3',      70368744177664:'g3',      140737488355328:'h3', 
    281474976710656:'a2',   562949953421312:'b2',    1125899906842624:'c2',   2251799813685248:'d2',   4503599627370496:'e2',    9007199254740992:'f2',    18014398509481984:'g2',   36028797018963968:'h2', 
    72057594037927936:'a1', 144115188075855872:'b1', 288230376151711744:'c1', 576460752303423488:'d1', 1152921504606846976:'e1', 2305843009213693952:'f1', 4611686018427387904:'g1', 9223372036854775808:'h1' 
}    


# TODO buggy!
# def countTrailingZeros(v):
#     res = np.int(np.log2(np.bitwise_xor(v,v - ONE)))
#     if res < 0:
#         res = 0
#     return res 

# TODO Move away from string op
def trailingZeros(s):
    s = np.binary_repr(s,width=64)
    return len(s) - len(s.rstrip('0'))

def strBBtoBB(str):
    bbStr = str.replace("\n","").replace(" ","")
    return np.uint64(int(bbStr,2))
    
def printBits(num, title=''):
    print()
    print(title)
    print()
    print(insert_newlines('{:064b}'.format(num), 8))
    print()

def insert_newlines(string, every=64):
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    lines.reverse()
    return '\n'.join(lines)

def reverse(s):
    s = np.binary_repr(s,width=64)
    return np.uint64(int(s[::-1], 2))
    
def makeField(row, col):
    colNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rowNames = ["8", "7", "6", "5", "4", "3", "2", "1"]
    return colNames[col] + rowNames[row]