N = int(input())
(*A,) = map(int, input().split())

ans = 0
p = 0
s = 0
max_step = 0

for a in A:
    s += a
    max_step = max(max_step, s)
    ans = max(ans, p + max_step)
    p += s

print(ans)
