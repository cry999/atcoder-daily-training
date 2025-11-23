N, D = map(int, input().split())

pos = [tuple(map(int, input().split())) for _ in range(N)]
visited = [False] * N

visited[0] = True
queue = [0]

while queue:
    i = queue.pop()
    xi, yi = pos[i]

    for j, (xj, yj) in enumerate(pos):
        if visited[j]:
            continue
        if (xi-xj)**2 + (yi-yj)**2 > D**2:
            # print(f'{i=}, {j=}: {(xi-xj)**2 + (yi-yj)**2} not reached')
            continue
        visited[j] = True
        queue.append(j)

for v in visited:
    print('YNeos'[not v::2])
