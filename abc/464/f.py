N, X = map(int, input().split())
(*A,) = map(int, input().split())

MOD = 998244353

inv = [1] * (N + 1)
inv_comb = [1] * (N + 1)  # N_C_k の逆元

for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-inv[r] * q) % MOD

for r in range(1, N + 1):
    inv_comb[r] = (inv_comb[r - 1] * r * inv[N - r + 1]) % MOD


def gen(a: list[int]):
    n = len(a)
    r = [[] for _ in range(n + 1)]
    r[0].append(0)

    for x in a:
        for k in range(n - 1, -1, -1):
            r[k + 1].extend(s + x for s in r[k])
    for rr in r:
        rr.sort()
    return r


# 半分全列挙で解く。
H = N // 2  # Half
tls, trs = gen(A[:H]), gen(A[H:])

a_all = sum(A) % MOD
ans = 0

for k, tr in enumerate(trs):
    pre = [0] * (len(tr) + 1)
    for i in range(len(tr)):
        pre[i + 1] = (pre[i] + tr[i]) % MOD

    for i, tl in enumerate(tls):
        if i + k == N:
            continue

        c = len(tr)
        coeff = inv[N - i - k] * inv_comb[i + k] % MOD
        p = 0
        for sl in tl:
            while c > 0 and sl + tr[c - 1] >= X:
                c -= 1

            p += (c * (a_all - sl) - pre[c]) % MOD
        ans = (ans + p * coeff) % MOD
print(ans)
