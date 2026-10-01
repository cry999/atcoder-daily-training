# >>> atcoder-stat >>>
# started_at  = 2026-10-01T10:08:37+09:00
# solved_at   = 2026-10-01T10:19:59+09:00
# duration_ms = 682745
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N = int(input())
prerequisites = [[]]
for _ in range(N):
    _, *p = map(int, input().split())
    prerequisites.append(p)

read = [False] * (N + 1)

ans = []

stack = [1]
while stack:
    target = stack[-1]
    if not prerequisites[target]:
        target = stack.pop()
        if not read[target]:
            ans.append(target)
            read[target] = True
    else:
        while prerequisites[target]:
            pre = prerequisites[target].pop()
            if not read[pre]:
                stack.append(pre)


ans.pop()
print(*ans)
