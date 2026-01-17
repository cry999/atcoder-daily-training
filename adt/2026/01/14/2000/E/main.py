N, Q = map(int, input().split())
balls = [i + 1 for i in range(N)]
rev_balls = {i + 1: i for i in range(N)}

for _ in range(Q):
    x = int(input())
    i = rev_balls[x]
    if i == N - 1:
        j = i - 1
    else:
        j = i + 1

    y = balls[j]
    balls[i], balls[j] = y, x
    rev_balls[x], rev_balls[y] = j, i

print(*balls)
