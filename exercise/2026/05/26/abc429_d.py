from bisect import bisect_right

N, M, C = map(int, input().split())
(*A,) = map(int, input().split())

A.sort()

# 1. i=0 とする。
# 2. x[i] = A[0] + ... + A[i] => C となるまで足し合わせる。
# ただし、A[i] = A[i+1] なら、C を超えてても足し合わせる。
# 3. x[i] を加算する。

# これを i=0 ~ M-1 まで繰り返すと M が大きいので無理。
i = 0
head = bisect_right(A, i) % N
tail = head

# print(*A)
s = 0
ans = 0
while i < M:
    while s < C:
        n = A[tail]
        s += 1
        tail += 1
        while tail < N and A[tail] == n:
            s += 1
            tail += 1
        tail %= N

    # print(f"{i=}: {s=} ({head=} -> {tail=}): ({A[head]=})")

    if i < A[head]:
        ans += s * (A[head] - i)
        i = A[head]
    else:
        ans += s * (M - i)
        i = M

    n = A[head]
    s -= 1
    head += 1
    while head < N and A[head] == n:
        s -= 1
        head += 1
    head %= N

print(ans)
