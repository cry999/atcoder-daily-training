# 全ての頂点の次数が 2 である必要がある。
# その後、ある点からスタートして
# 1. スタートまで辿り着ける
# 2. 全ての頂点を訪れている
# を満たせば良い。
#
# 計算量: O(N)

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    a, b = map(lambda x: int(x) - 1, input().split())
    g[a].append(b)
    g[b].append(a)

if len(g[0]) != 2:
    print("No")
    exit()

# s: スタート地点, p: 直前の頂点
s = g[0][0]
p = 0

visited = [False] * N
visited[0] = True

while True:
    # print(s)
    if len(g[s]) != 2:
        # print("[dim]")
        print("No")
        break
    if s == 0:
        # print("[s]")
        print("Yes" if all(visited) else "No")
        break
    if visited[s]:
        # print("[visited]")
        print("No")
        break

    visited[s] = True
    s, p = g[s][g[s][0] == p], s
