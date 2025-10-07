D, N = map(int, input().split())
hours = [24] * (D + 1)
hours[0] = 0

for i in range(N):
    L, R, H = map(int, input().split())
    for d in range(L, R+1):
        hours[d] = min(hours[d], H)

print(sum(hours))
