# >>> atcoder-stat >>>
# started_at  = 2026-09-03T14:52:24+09:00
# solved_at   = 2026-09-03T15:16:42+09:00
# duration_ms = 1458336
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())


ans = 0
left_x, right_x = 0, 0
left_y, right_y = 0, 0
for i in range(N):
    if A[i] > X:
        continue
    if A[i] < Y:
        continue

    left_x = max(left_x, i)
    while left_x < N and A[left_x] < X:
        left_x += 1

    if left_x == N or A[left_x] > X:
        continue

    right_x = max(right_x, left_x)
    while right_x < N and A[right_x] <= X:
        right_x += 1

    left_y = max(left_y, i)
    while left_y < N and A[left_y] > Y:
        left_y += 1

    if left_y == N or A[left_y] < Y:
        continue

    right_y = max(right_y, left_y)
    while right_y < N and A[right_y] >= Y:
        right_y += 1

    ans += max(0, min(right_x, right_y) - max(left_x, left_y))

print(ans)
