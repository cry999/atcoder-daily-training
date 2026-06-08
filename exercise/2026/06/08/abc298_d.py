from collections import deque
import sys

input = sys.stdin.readline

MOD = 998244353

Q = int(input())

head_pow10 = 1
inv_10 = pow(10, MOD - 2, MOD)
ans = 1
num = deque()
num.append(1)
for _ in range(Q):
    q, *args = map(int, input().split())

    if q == 1:
        x = args[0]
        head_pow10 = (head_pow10 * 10) % MOD
        ans = (ans * 10 + x) % MOD
        num.append(x)
    elif q == 2:
        x = num.popleft()
        ans = (ans - head_pow10 * x) % MOD
        head_pow10 = (head_pow10 * inv_10) % MOD
    else:
        print(ans)
