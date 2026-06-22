N, K = map(int, input().split())
(*A,) = map(int, input().split())

# 左端を固定すると、初めて A[l] + ... + A[r] が K を超えた r 以降
# は全て (l, r) 区間の和は K を超えるので条件を満たす。
# 尺取法。

l, r = 0, 0
s = 0
ans = 0
while l < N:
    r = max(r, l)
    while r < N and s < K:
        s += A[r]
        r += 1

    if s >= K:
        ans += N - r + 1
    else:
        break

    s -= A[l]
    l += 1

print(ans)
