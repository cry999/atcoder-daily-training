# >>> atcoder-stat >>>
# started_at  = 2026-07-05T11:39:32+09:00
# solved_at   = 2026-07-05T12:10:07+09:00
# duration_ms = 1835435
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
MOD = 998244353

(*N,) = map(int, input())
L = len(N)
M = int(input())
(*C,) = map(int, input().split())

STATE = 1 << 10

less_cnt = [0] * STATE
less_sum = [0] * STATE
same_cnt = [0] * STATE
same_sum = [0] * STATE

same_cnt[0] = 1

for i in range(L):
    n = N[i]

    n_less_cnt = [0] * STATE
    n_less_sum = [0] * STATE
    n_same_cnt = [0] * STATE
    n_same_sum = [0] * STATE

    for s in range(1 << 10):
        cnt, sum_ = less_cnt[s], less_sum[s]
        if cnt or sum_:
            for d in range(10):
                ns = s | (1 << d)
                if ns == (1 << 0):  # 0 だけはあり得ない
                    ns = 0
                n_less_cnt[ns] += cnt
                n_less_cnt[ns] %= MOD
                n_less_sum[ns] += sum_ * 10 + d * cnt
                n_less_sum[ns] %= MOD

        cnt, sum_ = same_cnt[s], same_sum[s]
        if cnt or sum_:
            for d in range(n + 1):
                ns = s | (1 << d)
                if ns == (1 << 0):  # 0 だけはあり得ない
                    ns = 0
                if d < n:
                    n_less_cnt[ns] += cnt
                    n_less_cnt[ns] %= MOD
                    n_less_sum[ns] += sum_ * 10 + d * cnt
                    n_less_sum[ns] %= MOD
                else:
                    n_same_cnt[ns] += cnt
                    n_same_cnt[ns] %= MOD
                    n_same_sum[ns] += sum_ * 10 + d * cnt
                    n_same_sum[ns] %= MOD

    less_cnt, less_sum = n_less_cnt, n_less_sum
    same_cnt, same_sum = n_same_cnt, n_same_sum

mask = 0
for c in C:
    mask |= 1 << c

ans = 0
for s in range(1 << 10):
    if s & mask != mask:
        continue

    cnt, sum_ = n_less_cnt[s], n_less_sum[s]
    if cnt > 0:
        ans += sum_
        ans %= MOD
    cnt, sum_ = n_same_cnt[s], n_same_sum[s]
    if cnt > 0:
        ans += sum_
        ans %= MOD
print(ans)
