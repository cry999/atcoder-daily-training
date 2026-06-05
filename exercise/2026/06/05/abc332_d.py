from itertools import permutations

H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]
B = [list(map(int, input().split())) for _ in range(H)]


def equal(a: list[list[int]], b: list[list[int]]):
    for i in range(H):
        for j in range(W):
            if a[i][j] != b[i][j]:
                return False
    return True


def inversion_number(a: list[int]):
    n = len(a)
    inv = 0
    for i in range(n):
        for j in range(i + 1, n):
            if a[i] > a[j]:
                inv += 1
    return inv


ans = float("inf")
for P in permutations(range(H)):
    inv_p = inversion_number(P)
    for Q in permutations(range(W)):
        inv_q = inversion_number(Q)
        C = [[A[P[h]][Q[w]] for w in range(W)] for h in range(H)]
        if equal(C, B):
            ans = min(ans, inv_p + inv_q)

if ans != float("inf"):
    print(ans)
else:
    print(-1)
