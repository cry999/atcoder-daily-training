from functools import cmp_to_key

N, K = map(int, input().split())

S = [input() for _ in range(N)]
S.sort(key=lambda x: (len(x), x), reverse=True)


def cmp(a: str, b: str) -> int:
    if a + b > b + a:
        return 1
    elif a + b < b + a:
        return -1
    else:
        return 0


def make(A: list[str]):
    A = sorted(A, key=cmp_to_key(cmp), reverse=True)
    return "".join(A).lstrip("0") or "0"


ans1 = make(S[:K])
ans2 = make(S[: K - 1] + [max(S[K - 1 :], key=int)])

if len(ans1) > len(ans2):
    print(ans1)
elif len(ans1) < len(ans2):
    print(ans2)
elif ans1 > ans2:
    print(ans1)
else:
    print(ans2)
