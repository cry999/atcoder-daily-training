N, Q = map(int, input().split())
(*X,) = map(int, input().split())

box = [0] * N
ans = [-1] * Q
for q in range(Q):
    if X[q] > 0:
        box[X[q] - 1] += 1
        ans[q] = X[q]
    else:
        min_x, min_i = float("inf"), 0
        for i in range(N):
            if box[i] < min_x:
                min_x = box[i]
                min_i = i
        box[min_i] += 1
        ans[q] = min_i + 1

print(*ans)
