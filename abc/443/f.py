from collections import deque


N = int(input())

dp = [-1 for _ in range(10 * N)]
backtrace = [-1 for _ in range(10 * N)]
q = deque([(0, 0)])

while q:
    x, c = q.popleft()
    idx = x * 10 + c

    for nc in range(max(1, c), 10):
        nx = (10 * x + nc) % N
        n_idx = nx * 10 + nc
        if dp[n_idx] != -1:
            # 既に訪問済み
            break

        dp[n_idx] = dp[idx] + 1
        backtrace[n_idx] = idx
        if nx == 0:
            # 最小の桁数とその時の末尾の数 (1 の位の数) を記録する
            idx = n_idx

            numbers = []
            while idx:
                numbers.append(idx % 10)
                idx = backtrace[idx]

            print("".join(chr(n + ord("0")) for n in numbers[::-1]))
            exit()
        q.append((nx, nc))

print(-1)
