from itertools import combinations
from functools import reduce


N, K = map(int, input().split())
*A, = map(int, input().split())


def xor(a: list[int]) -> int:
    return reduce(lambda x, y: x ^ y, a)


S = xor(A)
if K == N:
    print(S)
else:
    ans = max(xor(comb) ^ (0 if K < N-K else S)
              for comb in combinations(A, min(K, N-K)))
    print(ans)
