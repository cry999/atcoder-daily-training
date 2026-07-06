N = int(input())
guests = []  # 客が訪れる店 2 つ
points = []  # 入り口・出口の候補

for _ in range(N):
    a, b = map(int, input().split())
    guests.append((a, b))
    points.append(a)
    points.append(b)

ans = 10**18
for i in range(2 * N):
    entry = points[i]
    for j in range(2 * N):
        exit_ = points[j]

        score = 0
        for a, b in guests:
            score += abs(a - entry) + b - a + abs(exit_ - b)
        ans = min(ans, score)
print(ans)
