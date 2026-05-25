import sys

input = sys.stdin.readline
print = sys.stdout.write

MAX_ROW = MAX_COL = 2000

N = int(input())
sky = [[0] * (MAX_COL + 1) for _ in range(MAX_ROW + 1)]
clouds = []

for i in range(N):
    u, d, l, r = map(int, input().split())
    u, d, l, r = u - 1, d - 1, l - 1, r - 1
    clouds.append((u, d, l, r))

    sky[u][l] += 1
    sky[u][r + 1] -= 1
    sky[d + 1][l] -= 1
    sky[d + 1][r + 1] += 1

for r in range(MAX_ROW + 1):
    for c in range(MAX_COL):
        sky[r][c + 1] += sky[r][c]

for r in range(MAX_ROW):
    for c in range(MAX_COL + 1):
        sky[r + 1][c] += sky[r][c]


sunny = MAX_ROW * MAX_COL
for r in range(MAX_ROW + 1):
    for c in range(MAX_COL + 1):
        sunny -= sky[r][c] > 0
        sky[r][c] = sky[r][c] == 1

for r in range(MAX_ROW + 1):
    for c in range(MAX_COL):
        sky[r][c + 1] += sky[r][c]

for r in range(MAX_ROW):
    for c in range(MAX_COL + 1):
        sky[r + 1][c] += sky[r][c]

ans = []
for u, d, l, r in clouds:
    t = sunny
    removed = sky[d][r]
    if u - 1 >= 0:
        removed -= sky[u - 1][r]
    if l - 1 >= 0:
        removed -= sky[d][l - 1]
    if u - 1 >= 0 and l - 1 >= 0:
        removed += sky[u - 1][l - 1]

    ans.append(str(t + removed))
    ans.append("\n")

print("".join(ans))
