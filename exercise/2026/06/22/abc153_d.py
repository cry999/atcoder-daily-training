H = int(input())

n = 1
ans = 0

while H > 0:
    ans += n
    n <<= 1
    H >>= 1

print(ans)
