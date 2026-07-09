N, Q = map(int, input().split())
(*A,) = map(int, input().split())

MOD = 10**9 + 7


def mod_pow(base: int, exp: int):
    res = 1
    while exp > 0:
        if exp & 1:
            res = (res * base) % MOD
        base = (base * base) % MOD
        exp >>= 1
    return res


# dist[i] := 街 i と街 i+1 の距離
dist = [0] * (N - 1)
for i in range(N - 1):
    dist[i] = mod_pow(A[i], A[i + 1])

cum = [0] * N
for i in range(N - 1):
    cum[i + 1] = (cum[i] + dist[i]) % MOD

(*C,) = map(int, input().split())
C.append(1)

cur = 0
total_dist = 0
for c in C:
    c -= 1

    x, y = max(cur, c), min(cur, c)
    total_dist = (total_dist + cum[x] - cum[y]) % MOD
    cur = c
print(total_dist)
