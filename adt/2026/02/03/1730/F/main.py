N, M = map(int, input().split())

# 駒を置けないますの集合
cannot = set()

for _ in range(M):
    a, b = map(int, input().split())
    cannot.add((a, b))
    for sig_a in [-1, 1]:
        for sig_b in [-1, 1]:
            for diff_a, diff_b in [(1, 2), (2, 1)]:
                na, nb = a + sig_a * diff_a, b + sig_b * diff_b
                if 1 <= na <= N and 1 <= nb <= N:
                    cannot.add((na, nb))

print(N * N - len(cannot))
