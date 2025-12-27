# 求めるのは M^(K^N) である。
# フェルマーの小定理より M^(p-1) = 1 (mod p) なので、
# 指数は K^N = a (mod p-1) となる a を用いて
# M^(K^N) = M^a (mod p) と計算できる。

N, K, M = map(int, input().split())
MOD = 998244353

a = pow(K, N, MOD-1)
ans = pow(M, a, MOD)

print(f'{M % MOD=}, {a=}')

print(ans if M % MOD != 0 or a != 0 else 0)
