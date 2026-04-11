N, M = map(int, input().split())
(*C,) = map(int, input().split())

ans = 0
for _ in range(N):
    A, B = map(int, input().split())

    x = min(B, C[A - 1])
    C[A - 1] -= x
    ans += x

print(ans)
