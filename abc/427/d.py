T = int(input())

for _ in range(T):
    N, M, K = map(int, input().split())
    S = input()
    UV = {}
    for _ in range(M):
        U, V = map(int, input().split())
        UV.setdefault(U-1, []).append(V-1)

    # dp[n][k]: k ターン目に、n にいる場合の勝者
    dp = [[None] * (2*K+2) for _ in range(N)]

    for i in range(N):
        dp[i][2*K+1] = S[i]

    for k in range(2*K, -1, -1):
        # print(dp)
        for i in range(N):
            if k % 2 == 0:  # B の操作
                b_can_win = False
                for v in UV.get(i, []):
                    if dp[v][k+1] != 'B':
                        continue
                    b_can_win = True
                    break
                dp[i][k] = 'B' if b_can_win else 'A'

            else:  # A の操作
                a_can_win = False
                for v in UV.get(i, []):
                    if dp[v][k+1] != 'A':
                        continue
                    a_can_win = True
                    break
                dp[i][k] = 'A' if a_can_win else 'B'
    # print(dp)
    print('Alice' if dp[0][1] == 'A' else 'Bob')
