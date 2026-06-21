(*S,) = map(int, list(input()))
N = len(S)

MOD = 2019

pow10 = 10
suffix_mod = [0] * (N + 1)
counter = [0] * MOD
counter[0] = 1
for i in range(N, 0, -1):
    suffix_mod[i - 1] = (suffix_mod[i] + S[i - 1] * pow10) % MOD
    counter[suffix_mod[i - 1]] += 1
    pow10 = (pow10 * 10) % MOD

ans = 0
for n in range(N, -1, -1):
    counter[suffix_mod[n]] -= 1
    ans += counter[suffix_mod[n]]
print(ans)
