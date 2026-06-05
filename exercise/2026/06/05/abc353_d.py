MOD = 998244353


N = int(input())
(*A,) = map(int, input().split())

ans = 0
# f(i, j) で A[j] が足される部分の処理
for i in range(N):
    ans += (A[i] * i) % MOD
    ans %= MOD


# c: 係数。f(i, j) で A[i] が足される部分を考えるがこれは、i < j に対して
# A[j] の桁数を d[j] とすると A[i] * sum(10**(d[j]-1)) が影響する。
# これを c として蓄える。
c = 0
for i in range(N - 1, -1, -1):
    ans += (A[i] * c) % MOD
    ans %= MOD

    pow10 = 1
    while pow10 <= A[i]:
        pow10 *= 10

    c = (c + pow10) % MOD

print(ans)
