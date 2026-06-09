from itertools import permutations
from bisect import bisect_left

N, M = map(int, input().split())
S = [input() for _ in range(N)]
T = sorted(input() for _ in range(M))


def search(s: str):
    i = bisect_left(T, s)
    return i < M and T[i] == s


def special_join(ss: list[str]):
    s = "_".join(ss)
    if len(s) > 16 or len(s) < 3:
        return
    yield s

    if len(s) == 16:
        return

    for i in range(len(ss) - 1):
        tt = ss.copy()
        tt[i] = tt[i] + "_"
        yield from special_join(tt)


for perm in permutations(S):
    for s in special_join(list(perm)):
        if search(s):
            continue
        print(s)
        break
    else:
        continue
    break
else:
    print(-1)
