from collections import Counter

MOD = 10**9 + 7

N = int(input())
(*A,) = map(int, input().split())
MAX_A = max(A) + 1

# a 番目に並ぶ人でまだ後続が並んでいない人の数
s = Counter()
s[0] = 3

ans = 1
for a in A:
    ans = (ans * s[a]) % MOD
    s[a] -= 1
    s[a + 1] += 1

print(ans)
