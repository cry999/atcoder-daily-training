import sys

input = sys.stdin.readline

N, C = map(int, input().split())


sushi = []

for _ in range(N):
    x, v = map(int, input().split())
    sushi.append((x, v))

clockwise = [0] * (N + 1)
clockwise2 = [0] * (N + 1)  # 折り返し
for i in range(N):
    _, v = sushi[i]
    clockwise[i + 1] = clockwise[i] + v
    clockwise2[i + 1] = clockwise2[i] + v
# x は累積しないように注意
for i in range(N):
    x, _ = sushi[i]
    clockwise[i + 1] -= x
    clockwise2[i + 1] -= 2 * x
# i 番目をとるまでの最大値に変換
for i in range(N):
    clockwise[i + 1] = max(clockwise[i + 1], clockwise[i])
    clockwise2[i + 1] = max(clockwise2[i + 1], clockwise2[i])

anticlockwise = [0] * (N + 1)
anticlockwise2 = [0] * (N + 1)  # 折り返し
for i in range(N):
    _, v = sushi[N - 1 - i]
    anticlockwise[i + 1] = anticlockwise[i] + v
    anticlockwise2[i + 1] = anticlockwise2[i] + v
# x は累積しないように、また、逆回りなので、C-x になることに注意
for i in range(N):
    x, _ = sushi[N - 1 - i]
    anticlockwise[i + 1] -= C - x
    anticlockwise2[i + 1] -= 2 * (C - x)
# i 番目をとるまでの最大値に変換
for i in range(N):
    anticlockwise[i + 1] = max(anticlockwise[i + 1], anticlockwise[i])
    anticlockwise2[i + 1] = max(anticlockwise2[i + 1], anticlockwise2[i])

ans = 0
for i in range(N + 1):
    ans = max(ans, clockwise[i] + anticlockwise2[N - i])
    ans = max(ans, clockwise2[i] + anticlockwise[N - i])
print(ans)
