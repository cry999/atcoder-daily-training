from bisect import bisect_left
import sys

input = sys.stdin.readline
print = sys.stdout.write

N = int(input())
(*X,) = map(int, input().split())
(*P,) = map(int, input().split())

C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + P[i]

Q = int(input())
ans = [0] * Q
for q in range(Q):
    l, r = map(int, input().split())
    li = bisect_left(X, l)
    ri = bisect_left(X, r + 1)

    ans[q] = C[ri] - C[li]

print("\n".join(map(str, ans)) + "\n")
