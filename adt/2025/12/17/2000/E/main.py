from itertools import permutations
from math import factorial


N, K = map(int, input().split())
S = input()

if len(set(S)) == N:
    print(factorial(N))
    exit()

ans = 0
for perm in set(permutations(S)):
    for i in range(N-K+1):
        for k in range(K//2):
            if perm[i+k] != perm[i+K-(k+1)]:
                break
        else:
            # 回文発見
            break
    else:
        ans += 1
print(ans)
