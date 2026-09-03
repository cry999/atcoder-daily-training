# >>> atcoder-stat >>>
# started_at  = 2026-09-03T14:39:15+09:00
# solved_at   = 2026-09-03T14:48:59+09:00
# duration_ms = 584363
# target_ms   = 900000
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

# 偶数始まりと奇数始まりを試す
used = set()
ans = 0
for left in [0, 1]:
    right = left
    while left < N:
        right = max(right, left)
        print(f"[DEBUG] start {left=}, {right=}")

        while right + 1 < N and A[right] == A[right + 1] and A[right] not in used:
            used.add(A[right])
            right += 2
        print(f"[DEBUG] end {left=}, {right=}")
        if A[left] in used:
            used.remove(A[left])
        ans = max(ans, right - left)
        left += 2
print(ans)
