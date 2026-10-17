import sys

input = sys.stdin.readline


T = int(input())
for _ in range(T):
    N, M = map(int, input().split())
    L, R = [], []
    for _ in range(M):
        l, r = map(int, input().split())
        L.append(l)
        R.append(r)

    # 0 が確定した位置
    zero = [0] * (N + 1)
    stack = []

    for i in sorted(range(M), key=lambda i: (L[i], -R[i])):
        l, r = L[i] - 1, R[i]
        while stack and stack[-1][1] >= r:
            a, b = stack.pop()

            # [a, l) の範囲は 0 が確定
            zero[a] += 1
            zero[l] -= 1

            # [r, b) の範囲は 0 が確定
            zero[r] += 1
            zero[b] -= 1

        stack.append((l, r))

    K = len(stack)

    edges = []
    a, b, cover = 0, 0, 0

    for i in range(N):
        cover += zero[i]

        while b < K and stack[b][0] <= i:
            b += 1
        while a < K and stack[a][1] <= i:
            a += 1

        if cover == 0 and a < b:
            edges.append((a, b))

    s = [False] * (K + 1)
    s[0] = True
    for a, b in edges:
        if s[a]:
            s[b] = True

    t = [False] * (K + 1)
    t[K] = True
    for a, b in reversed(edges):
        if t[b]:
            t[a] = True

    cnt = [0] * (K + 1)
    for a, b in edges:
        if s[a] and t[b]:
            cnt[a] += 1
            cnt[b] -= 1

    c = 0
    for i in range(K):
        c += cnt[i]
        if c < 2:
            print("No")
            break
    else:
        print("Yes")
