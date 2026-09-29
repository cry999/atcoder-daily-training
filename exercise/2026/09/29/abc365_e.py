# >>> atcoder-stat >>>
# started_at  = 2026-09-29T14:57:32+09:00
# solved_at   = 2026-09-29T15:48:58+09:00
# duration_ms = 3086860
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

ans_bit = [0] * 61
for i in range(60):
    bit_cnt = [0, 0]
    for j in range(N - 2, -1, -1):
        if (A[j] >> i) & 1:
            bit_cnt[0], bit_cnt[1] = bit_cnt[1], bit_cnt[0]
        bit_cnt[((A[j] ^ A[j + 1]) >> i) & 1] += 1
        ans_bit[i] += bit_cnt[1]
    ans_bit[i + 1] += ans_bit[i] // 2
    ans_bit[i] %= 2

# print(ans_bit)

ans = 0
for i in range(61):
    ans |= ans_bit[i] << i
print(ans)
