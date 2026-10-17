N, W = map(int, input().split())
bento = []
for _ in range(N):
    a, b = map(int, input().split())
    bento.append((a, b))

ans = 0
for s in range(1 << N):
    total_weight = sum(bento[i][1] for i in range(N) if (s >> i) & 1)
    total_oisisa = sum(bento[i][0] for i in range(N) if (s >> i) & 1)
    if total_weight <= W:
        ans = max(ans, total_oisisa)
print(ans)
