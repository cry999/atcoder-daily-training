N, M = map(int, input().split())

cannot_use = set()
diffs = []
for si in [1, -1]:
    for sj in [1, -1]:
        diffs.append((si * 2, sj * 1))
        diffs.append((si * 1, sj * 2))

for _ in range(M):
    a, b = map(int, input().split())

    cannot_use.add((a, b))
    for di, dj in diffs:
        ni, nj = a + di, b + dj
        if not (1 <= ni <= N and 1 <= nj <= N):
            continue
        cannot_use.add((ni, nj))

print(N * N - len(cannot_use))
