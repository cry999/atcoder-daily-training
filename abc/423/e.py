# 累積わっぽいな...

N, Q = map(int, input().split())
A = list(map(int, input().split()))

c_i2 = [0] * (N+1)
c_i = [0] * (N+1)
c = [0] * (N+1)

for i in range(N):
    c_i2[i+1] = c_i2[i] + (i+1)*(i+1)*A[i]
    c_i[i+1] = c_i[i] + (i+1)*A[i]
    c[i+1] = c[i] + A[i]

for _ in range(Q):
    L, R = map(int, input().split())
    ans = -(c_i2[R] - c_i2[L-1]) + \
        (L+R)*(c_i[R] - c_i[L-1]) + \
        (1-L)*(1+R)*(c[R] - c[L-1])
    print(ans)
