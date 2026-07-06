n = int(input())
(*s,) = map(int, input().split())
q = int(input())
(*t,) = map(int, input().split())

ans = 0
for x in t:
    lo, hi = 0, n
    while hi > lo:
        mid = (hi + lo) // 2
        if s[mid] == x:
            lo = mid
            break
        elif s[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    if lo < n and s[lo] == x:
        ans += 1
print(ans)
