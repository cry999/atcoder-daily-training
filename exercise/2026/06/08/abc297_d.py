A, B = map(int, input().split())

ans = 0
while A != B:
    if B > A:
        A, B = B, A

    if A % B == 0:
        ans += A // B - 1
        break

    ans += A // B
    A %= B

print(ans)
