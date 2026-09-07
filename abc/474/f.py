N = int(input())
(*A,) = map(int, input().split())

# 全て同じになる数字は、少なくとも、max(A) 以上になる。
M = max(A)

# 約数が扱いやすいように 1-indexed にする

b = [0] * (N + 1)
c = [0] * (N + 1)

for i in range(N, 0, -1):
    # 倍数の影響を計算
    b[i] = M - A[i - 1] - sum(b[j] for j in range(2 * i, N + 1, i))
    c[i] = 1 - sum(c[j] for j in range(2 * i, N + 1, i))

INF = 10**18

# max(A) よりどれくらい大きいか?
lower, upper = 0, INF

for i in range(1, N + 1):
    if c[i] > 0:
        if b[i] < 0:
            lower = max(lower, (-b[i] + c[i] - 1) // c[i])
    elif c[i] == 0:
        if b[i] < 0:
            print(-1)
            exit()
    elif b[i] < 0:
        print(-1)
        exit()
    else:
        upper = min(upper, b[i] // (-c[i]))

if lower > upper:
    print(-1)
    exit()

print(M + lower - A[0])
