N = int(input())
*K, = map(int, input().split())

ans = float('inf')
for bit in range(1 << N):
    a, b = 0, 0
    for i in range(N):
        if (bit >> i) & 1:
            a += K[i]
        else:
            b += K[i]
    ans = min(max(a, b), ans)
print(ans)
