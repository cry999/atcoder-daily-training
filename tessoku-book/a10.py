N = int(input())
A = list(map(int, input().split()))

max_from_l = [0] * (N+2)
for i in range(N):
    max_from_l[i+1] = max(max_from_l[i], A[i])

max_from_r = [0] * (N+2)
for i in range(N-1, -1, -1):
    max_from_r[i+1] = max(max_from_r[i+2], A[i])

# print(max_from_l)
# print(max_from_r)


D = int(input())
for _ in range(D):
    L, R = map(int, input().split())
    print(max(max_from_l[L-1], max_from_r[R+1]))
