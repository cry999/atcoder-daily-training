n = int(input())
color = [0] * 1_000_002

for _ in range(n):
    a, b = map(int, input().split())
    color[a] += 1
    color[b+1] -= 1

for i in range(1, 1_000_002):
    color[i] += color[i-1]

print(max(color))
