N, Q = map(int, input().split())
(*A,) = map(int, input().split())

prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + A[i]

chunk_sum = [0] * (N + 1)
for i in range(N):
    chunk_sum[i + 1] = chunk_sum[i] + prefix[i + 1]


def index(i: int):
    lo, hi = 0, N
    while hi - lo > 1:
        x = (lo + hi) // 2
        if x * (x + 1) // 2 < i:
            lo = x
        else:
            hi = x
    return lo


for _ in range(Q):
    l, r = map(int, input().split())
    chunk_l = index(l)
    i1 = l - chunk_l * (chunk_l + 1) // 2

    chunk_r = index(r)
    i2 = r - chunk_r * (chunk_r + 1) // 2

    if chunk_l == chunk_r:
        print(prefix[i2] - prefix[i1 - 1])
    else:
        ans = chunk_sum[chunk_r] - chunk_sum[chunk_l + 1]
        ans += prefix[i2] + (prefix[chunk_l + 1] - prefix[i1 - 1])
        print(ans)
