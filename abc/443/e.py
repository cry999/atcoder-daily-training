from collections import deque


T = int(input())

for _ in range(T):
    N, C = map(int, input().split())
    # print(f"=== Test case {_ + 1} ===")
    S = [input() for _ in range(N)]
    S.reverse()

    cum = [[0] * N for _ in range(N + 1)]
    for i in range(N):
        for j in range(N):
            cum[i + 1][j] = cum[i][j] + int(S[i][j] == ".")

    queue = deque([(0, C - 1)])

    visited = [[False] * N for _ in range(N)]

    # print(f"{cum=}")

    while queue:
        n, c = queue.popleft()
        # print(n, c)

        for nn, nc in [(n + 1, c - 1), (n + 1, c), (n + 1, c + 1)]:
            if not (0 <= nc < N and 0 <= nn < N):
                continue

            if visited[nn][nc]:
                continue

            # print(f" check{nn=}, {nc=}, {cum[nn][nc]=}")
            if cum[nn][nc] == nn:
                # 今の位置より下が全て '.' ならそれより上は全通過可能
                for k in range(nn, N):
                    if visited[k][nc]:
                        continue
                    visited[k][nc] = True
                    queue.append((k, nc))
                continue

            if S[nn][nc] == "#":
                continue

            visited[nn][nc] = True
            queue.append((nn, nc))

    print("".join(["1" if t else "0" for t in visited[-1]]))
