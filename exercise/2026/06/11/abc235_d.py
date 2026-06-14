from collections import deque

a, N = map(int, input().split())

upper = 1
while upper <= N:
    upper *= 10

q = deque()
q.append(1)

operation = [-1] * (upper + 1)
operation[1] = 0

while q:
    x = q.popleft()

    if x * a <= upper and operation[x * a] == -1:
        operation[x * a] = operation[x] + 1
        if x * a == N:
            break
        q.append(x * a)

    if x >= 10 and x % 10:
        w, z = divmod(x, 10)
        d = 1
        while d <= w:
            d *= 10
        y = z * d + w
        if y <= upper and operation[y] == -1:
            operation[y] = operation[x] + 1
            if y == N:
                break
            q.append(y)

print(operation[N])
