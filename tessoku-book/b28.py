MOD = 10**9 + 7
N = int(input())

a1, a2 = 1, 1
i = 3
an = a1 + a2
while i <= N:
    an = (a1 + a2) % MOD
    a1, a2 = a2, an
    i += 1
print(an)
