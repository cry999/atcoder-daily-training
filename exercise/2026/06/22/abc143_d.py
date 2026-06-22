N = int(input())
L = sorted(map(int, input().split()))

# a <= b <= c とすることで、a < b + c と b < c + a は必然的に成り立つ。
# (a > 0, b > 0 であることに注意)
# よって c < a + b だけ満たすことを確認すれば良い。

ans = 0
for i in range(N):
    a = L[i]
    k = i + 1
    for j in range(i + 1, N):
        b = L[j]
        k = max(k, j)
        while k < N and L[k] < a + b:
            k += 1

        ans += k - j - 1
print(ans)
