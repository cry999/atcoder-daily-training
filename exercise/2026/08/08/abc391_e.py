# >>> atcoder-stat >>>
# started_at  = 2026-08-08T17:19:15+09:00
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input())


f = [1] * (3**N)
a = A[:]
for k in range(N):
    for i in range(3 ** (N - k - 1)):
        ch = a[3 * i : 3 * i + 3]
        pr = int(sum(ch) >= 2)

        if len(set(ch)) == 1:
            f[i] = sum(sorted(f[3 * i : 3 * i + 3])[:2])
        else:
            f[i] = min(f[3 * i + j] for j in range(3) if ch[j] == pr)

        a[i] = pr


print(f[0])
