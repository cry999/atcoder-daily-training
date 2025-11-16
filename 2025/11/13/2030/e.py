N, K = map(int, input().split())

counts = {}

for i in range(N):
    S = input()
    counts[i] = {}
    for c in S:
        counts[i][c] = counts[i].get(c, 0) + 1

max_k_count = 0
for i in range(1 << N):
    tmp_counts = {}
    for k in range(N):
        if not (i >> k) & 1:
            continue
        for c, v in counts[k].items():
            tmp_counts[c] = tmp_counts.get(c, 0) + v
    k_count = 0
    for v in tmp_counts.values():
        if v == K:
            k_count += 1
    max_k_count = max(max_k_count, k_count)

print(max_k_count)
