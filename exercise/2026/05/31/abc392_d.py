from collections import defaultdict
from itertools import combinations

N = int(input())
# hist[i][x] := i 番目のダイスがもつ x の書かれた面の数
hist = [defaultdict(int) for _ in range(N)]
num_of_sides = [0] * N

for i in range(N):
    num_of_sides[i], *a = map(int, input().split())

    for x in a:
        hist[i][x] += 1

ans = 0
for a1, a2 in combinations(range(N), 2):
    k1, k2 = num_of_sides[a1], num_of_sides[a2]

    p = 0
    for x, n1 in hist[a1].items():
        if x not in hist[a2]:
            continue
        n2 = hist[a2][x]
        p += n1 * n2 / k1 / k2
    ans = max(ans, p)
print(ans)
