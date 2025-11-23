N, M = map(int, input().split())
*A, = map(int, input().split())

# mods[d][n] := 任意の i について A[i] * 10^(d-1) を M で割ったあまりが n に等しいもののカウント
mods = [dict() for _ in range(11)]

for i, a in enumerate(A):
    for j in range(11):
        a %= M
        mods[j][a] = mods[j].get(a, 0)+1
        a *= 10

# print(mods)
# print(A)
ans = 0
for a in A:
    digit = 0
    while a >= 10**digit:
        digit += 1

    ans += mods[digit].get((M-(a % M)) % M, 0)
print(ans)
