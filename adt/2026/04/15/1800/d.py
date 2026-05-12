from collections import deque

R, C = map(int, input().split())
B = [input() for _ in range(R)]
A = [[""] * C for _ in range(R)]

for r in range(R):
    for c in range(C):
        if B[r][c] in "123456789":
            b = int(B[r][c])
            q = deque([(r, c, b)])
            visited = [[False] * C for _ in range(R)]
            visited[r][c] = True

            while q:
                rr, cc, rest = q.popleft()
                A[rr][cc] = "."
                if rest == 0:
                    continue

                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = rr + dr, cc + dc
                    if not (0 <= nr < R and 0 <= nc < C):
                        continue
                    if visited[nr][nc]:
                        continue
                    visited[nr][nc] = True
                    if rest > 0:
                        q.append((nr, nc, rest - 1))
for r in range(R):
    for c in range(C):
        if A[r][c] == "":
            A[r][c] = B[r][c]

for r in A:
    print("".join(r))
