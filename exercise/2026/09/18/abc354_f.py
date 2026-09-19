# >>> atcoder-stat >>>
# started_at  = 2026-09-18T11:28:04+09:00
# solved_at   = 2026-09-18T11:44:47+09:00
# duration_ms = 1003627
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left
import sys

input = sys.stdin.readline
INF = 10**18

# 考察
# 1. A[i] が最長の増加部分列に含まれるか、と言う問題を A[i] を含む最長の増加部分列の長さは何か？に変える
# 2. 1 を求めた後に、1 の答えの最大値が一致するものを答えとすれば良い。
# 3. 1 をどう求めるか?
# 3.a. 左から最長増加部分列を求めながら、A[i] の左に連なる最長の列の長さをメモする
# 3.b. 同様にして右から最長減少部分列を求めながら、A[i] の右に連なる最長の列の長さをメモする
# 3.c. i の左と右の長さ + 1 を A[i] を含む最長列の長さとして記録する。

T = int(input())
for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    left = [0] * N
    right = [0] * N

    # まずは左から最長増加部分列を求めながら A[i] を含む左の列の長さを調べる
    length = [INF] * (N + 1)
    length[0] = 0
    for i in range(N):
        j = bisect_left(length, A[i])
        length[j] = A[i]
        left[i] = j - 1

    # 次に右から最長減少部分列を求めながら A[i] を含む右の列の長さを調べる
    length[:] = [0] * (N + 1)
    length[0] = -INF
    for i in range(N - 1, -1, -1):
        j = bisect_left(length, -A[i])
        length[j] = -A[i]
        right[i] = j - 1

    print(f"[DEBUG] {left=}, {right=}")

    max_len = max(l + r for l, r in zip(left, right))
    ans = [i + 1 for i in range(N) if left[i] + right[i] == max_len]
    print(len(ans))
    print(*ans)
