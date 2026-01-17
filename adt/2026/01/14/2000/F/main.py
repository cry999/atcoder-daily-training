N, K = map(int, input().split())

(*A,) = map(int, input().split())

if K % 2 == 0:
    ans = 0
    for i in range(K // 2):
        ans += A[2 * i + 1] - A[2 * i]
    print(ans)
else:
    prefix_sum = [0] * (K // 2 + 1)
    for i in range(K // 2):
        prefix_sum[i + 1] = prefix_sum[i] + A[2 * i + 1] - A[2 * i]
    suffix_sum = [0] * (K // 2 + 1)
    for i in range(K // 2 - 1, -1, -1):
        suffix_sum[i] = suffix_sum[i + 1] + A[2 * i + 2] - A[2 * i + 1]

    ans = prefix_sum[K // 2]
    for i in range(K // 2):
        ans = min(ans, prefix_sum[i] + suffix_sum[i])
    print(ans)
