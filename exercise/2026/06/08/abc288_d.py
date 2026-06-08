import sys

input = sys.stdin.readline

N, K = map(int, input().split())
(*A,) = map(int, input().split())
A.append(0)


S = [0] * (N + 1)
for i in range(N + 1):
    S[i] = A[i]
    if i >= K:
        S[i] += S[i - K]


Q = int(input())
for _ in range(Q):
    l, r = map(int, input().split())
    l -= 1
    r -= 1

    values = []
    for i in range(l, min(l + K, r + 1)):
        right = i + ((r - i) // K) * K

        total = S[right]
        if i >= K:
            total -= S[i - K]

        values.append(total)

    print("Yes" if len(set(values)) == 1 else "No")
