from collections import deque
import sys

input = sys.stdin.readline

N, M = map(int, input().split())
g = [set() for _ in range(N + 1)]

dim = [0] * (N + 1)
for _ in range(M):
    k = int(input())
    (*A,) = map(int, input().split())
    for i in range(k - 1):
        if A[i] not in g[A[i + 1]]:
            g[A[i + 1]].add(A[i])
            dim[A[i]] += 1

visited = [False] * (N + 1)
q = deque()

for i in range(1, N + 1):
    if dim[i] == 0:
        q.append(i)
        visited[i] = True


def bfs():
    node_num = 0
    while q:
        u = q.popleft()
        node_num += 1

        for v in g[u]:
            if visited[v]:
                return 0
            dim[v] -= 1
            if dim[v] == 0:
                q.append(v)
                visited[v] = True

    return node_num


print("Yes" if bfs() == N else "No")
