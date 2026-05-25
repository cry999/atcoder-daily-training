import sys

input = sys.stdin.buffer.readline

N, M = map(int, input().split())
A = list(map(int, input().split()))

# digits[i] := A[i] の桁数
digits = [len(str(a)) for a in A]
used_digits = set(digits)

# あらかじめ剰余にしておく
remainders = [a % M for a in A]

# pow10[d] := 10^d mod M
max_digit = max(used_digits)
pow10 = [1] * (max_digit + 1)
for d in range(1, max_digit + 1):
    pow10[d] = pow10[d - 1] * 10 % M

# hist[d][r] := (x * 10^d) % M == r となる x の個数
# 必要な桁数 d についてだけ作る
hist = {}

for d in used_digits:
    p = pow10[d]
    h = {}

    for x in remainders:
        r = x * p % M
        h[r] = h.get(r, 0) + 1

    hist[d] = h

ans = sum(hist[d].get((-a) % M, 0) for a, d in zip(A, digits))

sys.stdout.write(str(ans) + "\n")
