N, M = map(int, input().split())
(*A,) = map(int, input().split())
A.sort(reverse=True)

prime_factors = []  # 使用不可能な素因数
is_prime = [True] * (10**5 + 1)
available = [True] * (10**5 + 1)

for a in A:
    available[a] = False

for i in range(2, 10**5 + 1):
    if not is_prime[i]:
        continue

    for j in range(i * 2, 10**5 + 1, i):
        is_prime[j] = False

        # A に含まれている要素が i の倍数にあれば素数 i は利用不可
        available[i] = available[i] and available[j]

    if not available[i]:
        prime_factors.append(i)

ans = [True] * (M + 1)
ans[0] = False

for p in prime_factors:
    for pp in range(p, M + 1, p):
        ans[pp] = False

print(sum(ans))
for p in range(M + 1):
    if ans[p]:
        print(p)
