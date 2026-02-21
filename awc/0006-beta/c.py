from math import ceil

N, M, D = map(int, input().split())
(*T,) = map(int, input().split())

cooler_packs = 0
for t in T:
    cooler_packs += ceil(max(t - M, 0) / D)

print(cooler_packs)
