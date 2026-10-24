# >>> atcoder-stat >>>
# started_at  = 2026-10-24T09:30:54+09:00
# solved_at   = 2026-10-24T09:43:35+09:00
# duration_ms = 761445
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left

N, Q = map(int, input().split())
(*A,) = map(int, input().split())

prefix_sum = [0] * (N + 1)
for i in range(N):
    prefix_sum[i + 1] = prefix_sum[i] + A[i]

prefix_sum_2 = [0] * (N + 1)
for i in range(N):
    prefix_sum_2[i + 1] = prefix_sum_2[i] + prefix_sum[i + 1]

chunk_size = [n * (n + 1) // 2 for n in range(N + 1)]


def get_sum(i: int):
    j = bisect_left(chunk_size, i)
    if i == chunk_size[j]:  # 全部含む
        return prefix_sum_2[j]
    print(f"[DEBUG] {i=} {j=} {chunk_size[j]=}")
    return prefix_sum_2[j - 1] + prefix_sum[i - chunk_size[j - 1]]


for _ in range(Q):
    L, R = map(int, input().split())

    upper = get_sum(R)
    lower = get_sum(L - 1)

    print(f"[DEBUG] {L=} {R=} {lower=} {upper=} {get_sum(2)=}")
    print(upper - lower)
