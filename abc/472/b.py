N = int(input())
(*L,) = map(int, input().split())

left = 0
right = sum(L)
ans = right - left
for i in range(N):
    left += L[i]
    right -= L[i]
    ans = min(ans, abs(left - right))
print(ans)
