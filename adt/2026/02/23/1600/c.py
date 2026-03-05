N, Q = map(int, input().split())
(*X,) = map(int, input().split())

balls = [0] * N
ans = [0] * Q

for i, x in enumerate(X):
    if x > 0:
        ans[i] = x
        balls[x - 1] += 1
    else:
        c = balls.index(min(balls))
        ans[i] = c + 1
        balls[c] += 1

print(*ans)
