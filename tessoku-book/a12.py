N, K = map(int, input().split())
A = list(map(int, input().split()))

# left, right = 1, K * max(A) + 1
left, right = 1, 10**9
while left <= right:
    # print(left, right)
    mid = (left + right) // 2
    printed = sum(mid // a for a in A)
    # 同じ値のときは左側を探索
    if printed >= K:
        right = mid - 1
    else:
        left = mid + 1

print(left)
