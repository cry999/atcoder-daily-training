N, K, T = map(int, input().split())

exp = 0
for _ in range(N):
    D, R = map(int, input().split())
    if R < K * D:
        continue
    exp += R
if exp >= T:
    print("Yes")
else:
    print("No")
