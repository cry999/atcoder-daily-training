from atcoder.fenwicktree import FenwickTree

N = int(input())
(*A,) = map(int, input().split())

lo, hi = 0, max(A) + 1

while hi - lo > 1:
    # X 以下の数字が中央値になるかどうか？
    # -> X 以下の数字が過半数を占める部分列が部分列全体の過半数以上存在するか？
    X = (lo + hi) // 2

    C = [0] * (N + 1)
    for i in range(N):
        C[i + 1] = C[i] + (A[i] <= X)

    c = 0
    bit = FenwickTree(2 * N + 1)
    bit.add(N, 1)

    for i in range(1, N + 1):
        x = 2 * C[i] - i + N
        c += bit.sum(0, x)
        bit.add(x, 1)
    print(f"[DEBUG] {c=}")

    M = N * (N + 1) // 2  # 部分列の総数
    if M - c < c:  # X 以下の数字が過半数を占める部分列が、部分列全体の過半数以上
        hi = X
    else:
        lo = X

print(hi)
