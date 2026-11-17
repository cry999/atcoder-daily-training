from collections import defaultdict
from itertools import combinations
from math import comb

N, M = map(int, input().split())
S = [input() for _ in range(N)]

if M == 2:
    print(N * (N - 1) // 2)
else:
    ans = 0

    for d in range(3):
        c = comb(M - 3 + d, d)
        if d % 2:
            c *= -1

        masks = [
            sum(255 << (8 * j) for j in i) for i in combinations(range(M), M - 2 + d)
        ]
        counter: defaultdict[int, int] = defaultdict(int)
        for s in S:
            x = int.from_bytes(s.encode(), "little")
            for mask in masks:
                counter[(mask << 48) | (x & mask)] += 1

        p = sum(v * (v - 1) // 2 for v in counter.values())
        ans += c * p
    print(ans)
