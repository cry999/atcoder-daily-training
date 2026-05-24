N = int(input())
(*A,) = map(int, input().split())

length = {}

ans = 0
for a in A:
    length[a] = max(length.get(a, 1), length.get(a - 1, 0) + 1)
    ans = max(ans, length[a])

print(ans)
