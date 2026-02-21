N, K = map(int, input().split())
(*H,) = sorted(map(int, input().split()), reverse=True)

# 時間のかかる K こは爆破する。
ans = min(K, N)

for i in range(min(K, N), N):
    ans += H[i]

print(ans)
