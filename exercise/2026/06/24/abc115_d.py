N, X = map(int, input().split())

# f[i] = レベル i バーガーの層の総数
# f[i+1] = 2*f[i] + 3 -> f[i] = 2^{i+2}-3
f = [1] * (50 + 1)
for i in range(50):
    f[i + 1] = 2 * f[i] + 3

# p[i] = レベル i バーガーの層のうち、パティの層の総数
# p[i+1] = 2*p[i] + 1 -> p[i] = 2^{i+1}-1
p = [1] * (50 + 1)
for i in range(50):
    p[i + 1] = 2 * p[i] + 1

ans = 0
while True:
    print(f"[DEBUG] {N=}, {X=}, {ans=}, {f[N]=}")
    if X == f[N]:
        print(f"[DEBUG]   top! {f[N]=}")
        ans += p[N]
        break
    elif X > f[N - 1] + 2:
        print(f"[DEBUG]   between top and middle {f[N-1]+2=}")
        ans += p[N - 1] + 1
        X -= f[N - 1] + 2
        N -= 1
    elif X == f[N - 1] + 2:
        print(f"[DEBUG]   middle {f[N-1]+2=}")
        ans += p[N - 1] + 1
        break
    elif X > 1:
        print(f"[DEBUG]   between middle ({f[N-1]+2}) and bottom {1=}")
        X -= 1
        N -= 1
    else:
        print(f"[DEBUG]   bottom {1=}")
        break
print(ans)
