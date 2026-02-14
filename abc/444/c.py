from bisect import bisect_left as bl


N = int(input())
(*A,) = map(int, input().split())

A.sort()

max_a = A[-1]

# L の候補は max_a か max_a + min_a
ans = []

L = max_a + A[0]
if N % 2 == 0 and all(A[j] + A[N - j - 1] == L for j in range(N // 2)):
    ans.append(L)

# L = max_a の場合は、max_a の長さのものを全てのぞいて
# 偶数本残っている
i = bl(A, max_a)
L = max_a
if i % 2 == 0 and all(A[j] + A[i - j - 1] == L for j in range(i // 2)):
    ans.append(L)

print(*sorted(ans))
