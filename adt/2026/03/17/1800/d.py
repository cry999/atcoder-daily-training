from atcoder.modint import Modint, ModContext

with ModContext(998244353):
    A, B, C, D, E, F = map(lambda x: Modint(int(x)), input().split())
    print((A * B * C - D * E * F).val())
