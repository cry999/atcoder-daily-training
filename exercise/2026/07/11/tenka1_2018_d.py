from itertools import combinations
from math import isqrt

N = int(input())

d = isqrt(8 * N + 1)
if d * d != 8 * N + 1:
    print("No")
else:
    print("Yes")
    # 8N+1 が奇数なので、d も奇数。すなわち 1+d は必ず 2 で割り切れる
    k = (1 + d) // 2
    print(k)
    S = [[] for _ in range(k)]
    for n, comb in enumerate(combinations(range(k), 2)):
        i, j = comb
        S[i].append(n + 1)
        S[j].append(n + 1)

    for s in S:
        print(len(s), *s)
