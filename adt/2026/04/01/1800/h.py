N = int(input())
M = 100

# small_cubes[x][y][z]: (x, y, z) - (x+1,y+1,z+1) を対角線にもつ立方体が、どの直方体に含まれるか保持
small_cubes = [[[-1] * (M + 1) for _ in range(M + 1)] for _ in range(M + 1)]

for i in range(N):
    x1, y1, z1, x2, y2, z2 = map(int, input().split())

    for x in range(x1, x2):
        for y in range(y1, y2):
            for z in range(z1, z2):
                small_cubes[x][y][z] = i

adj = [set() for _ in range(N)]

for x in range(M):
    for y in range(M):
        for z in range(M):
            # 一つ目の立方体の番号
            i = small_cubes[x][y][z]
            if i == -1:
                continue
            # x-1, y-1, z-1 は他の立方体から見た x+1, y+1, z+1 と同じなので
            # 計算に入れない。

            for j in [
                small_cubes[x + 1][y][z],
                small_cubes[x][y + 1][z],
                small_cubes[x][y][z + 1],
            ]:
                if j != -1 and i != j:
                    adj[i].add(j)
                    adj[j].add(i)

for a in adj:
    print(len(a))
