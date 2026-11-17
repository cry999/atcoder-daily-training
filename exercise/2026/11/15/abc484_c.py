# >>> atcoder-stat >>>
# started_at  = 2026-11-15T09:18:38+09:00
# solved_at   = 2026-11-15T12:32:31+09:00
# duration_ms = 11633427
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())


def solve(A: list[int], B: list[int]):
    diff_0 = [-1] * (N + 1)
    diff_0[0] = 0
    for i in range(N):
        diff_0[i + 1] = diff_0[i] + (A[i] != B[i])

    diff_1 = [-1] * (N + 1)
    diff_1[0] = 0
    for i in range(N - 1):
        diff_1[i + 1] = diff_1[i] + (A[i + 1] != B[i])

    print(f"[DEBUG] {diff_0=}")
    print(f"[DEBUG] {diff_1=}")

    i = 0
    while i + 1 <= N and diff_0[i + 1] == 0:
        i += 1

    j = i
    while j + 1 < N and diff_1[j + 1] == diff_1[i]:
        j += 1

    print(f"[DEBUG] {i=}, {j=}")
    return i == N or (A[i] == B[j] and diff_0[N] == diff_0[j + 1])


if solve(A, B) or solve(B, A):
    print("Yes")
else:
    print("No")
