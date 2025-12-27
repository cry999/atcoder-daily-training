N = int(input())
*A, = map(int, input().split())
*B, = map(int, input().split())
*C, = map(int, input().split())

SA = [0] * (N+1)
SB = [0] * (N+1)
SC = [0] * (N+1)

for i in range(N):
    SA[i+1] = SA[i] + A[i]
    SB[i+1] = SB[i] + B[i]
    SC[i+1] = SC[i] + C[i]

# SBC[y] = i >= y における SB[i]-SC[i] の最大値
# SBC[N] は y < N の条件より考慮不要
SBC = [0]*N
for i in range(N-1, -1, -1):
    SBC[i] = SB[i]-SC[i]
    if i+1 < N:
        SBC[i] = max(SBC[i], SBC[i+1])
# print(*SB)
# print(*SC)
# print(*SBC)

ans = 0
for x in range(1, N-1):
    # for y in range(x+1, N):
    #     print(f'{x=}, {y=}, {SA[x]+(SB[y]-SB[x])+(SC[N]-SC[y])}')
    #     ans = max(ans, SA[x]+(SB[y]-SB[x])+(SC[N]-SC[y]))
    #     t = SC[N]+(SA[x]-SB[x])+(SB[y]-SC[y])
    ans = max(ans, SC[N]+(SA[x]-SB[x])+SBC[x+1])

print(ans)
