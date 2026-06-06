N, K, M = map(int, input().split())
max_by_color = [0] * N
others = []

for _ in range(N):
    c, v = map(int, input().split())
    if max_by_color[c - 1] < v:
        others.append(max_by_color[c - 1])
        max_by_color[c - 1] = v
    else:
        others.append(v)

max_by_color.sort(reverse=True)

ans = 0
for i in range(N):
    if max_by_color[i] == 0:
        break
    if i < M:
        ans += max_by_color[i]
    else:
        others.append(max_by_color[i])

others.sort(reverse=True)

for i in range(K - M):
    ans += others[i]

print(ans)
