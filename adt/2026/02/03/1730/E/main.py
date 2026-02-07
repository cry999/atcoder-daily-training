N = int(input())
(*P,) = map(int, input().split())

for i in range(N - 1, 0, -1):
    if P[i - 1] < P[i]:
        continue
    # i 番目以降で P[i-1] 未満の最大値を探す。
    p = -1
    index = -1
    for j in range(i, N):
        if P[j] < P[i - 1] and p < P[j]:
            p, index = P[j], j
    P[i - 1], P[index] = P[index], P[i - 1]
    print(*(P[:i] + sorted(P[i:], reverse=True)))
    break
