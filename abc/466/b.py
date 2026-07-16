N, M = map(int, input().split())
max_size = [-1] * M

for _ in range(N):
    c, s = map(int, input().split())
    max_size[c - 1] = max(max_size[c - 1], s)
print(*max_size)
