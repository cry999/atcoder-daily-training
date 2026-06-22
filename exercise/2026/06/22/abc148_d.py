N = int(input())
(*A,) = map(int, input().split())

j = 1
ans = 0
for a in A:
    if a == j:
        j += 1
    else:
        ans += 1

print(ans if ans < N else -1)
