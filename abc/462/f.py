import sys

input = sys.stdin.readline


T = int(input())

# CHARS = "ABCX"
# 0: A, 1: B, 2: C, 3: X(ABC 以外の任意の文字) として扱う。
A = 0
B = 1
C = 2
X = 3
CHARS = [0, 1, 2, 3]

INF = 10**9


compute_next_last2 = [
    [1, 0, 0, 0],
    [1, 2, 0, 0],
    [1, 0, 0, 0],
]


for _ in range(T):
    S = input().rstrip()
    K = int(input())

    N = len(S)
    SS = [0] * N
    for i in range(N):
        SS[i] = 0 if S[i] == "A" else 1 if S[i] == "B" else 2 if S[i] == "C" else 3

    dp = [INF] * (3 * (K + 1))
    dp[0] = 0

    pre_old_is = [
        i >= 2 and SS[i - 2] == A and SS[i - 1] == B and SS[i] == C for i in range(N)
    ]

    for i, s in enumerate(SS):
        nxt = [INF] * (3 * (K + 1))

        for j in range(3 * (K + 1)):
            delta, last2 = divmod(j, 3)

            cur = dp[j]
            if cur == INF:
                continue

            for c in CHARS:
                # i 文字目を c にするコスト
                if c == X:
                    # 変更後が X (ABC 以外の任意の文字) の場合:
                    # 変更前が A, B, C の場合だけ変更する価値があるのでコスト 1
                    # それ以外の場合は、X と同等なので変換はせずコスト 0
                    add_cost = 0 if s == X else 1
                else:
                    # 変更前が ABC のいずれかの場合:
                    # 変更前後で同じならコスト 0, 異なるならコスト 1
                    add_cost = 0 if s == c else 1

                # 変更前の文字列の最後の 3 文字が ABC か?
                old_is = pre_old_is[i]
                # 変更後の文字列の最後の 3 文字が ABC か?
                new_is = last2 == 2 and c == C

                nxt_delta = delta + new_is - old_is
                nxt_last2 = compute_next_last2[last2][c]

                if not (0 <= nxt_delta <= K):
                    continue

                if nxt[nxt_delta * 3 + nxt_last2] > cur + add_cost:
                    nxt[nxt_delta * 3 + nxt_last2] = cur + add_cost

        dp = nxt

    ans = -1
    for j in range(3):
        if dp[K * 3 + j] != INF:
            if ans == -1 or dp[K * 3 + j] < ans:
                ans = dp[K * 3 + j]
    print(ans)
