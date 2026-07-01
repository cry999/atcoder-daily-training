T = int(input())

for _ in range(T):
    N, W = map(int, input().split())

    weight = []
    values = []
    for _ in range(N):
        w, v = map(int, input().split())
        weight.append(w)
        values.append(v)

    pre_w = [0] * (N + 1)
    pre_v = [0] * (N + 1)

    for i in range(N):
        pre_w[i + 1] = pre_w[i] + weight[i]
        pre_v[i + 1] = pre_v[i] + values[i]

    def solve(n: int, w: int):
        if n == 0:
            return 0
        if pre_w[n] <= w:
            return pre_v[n]
        if weight[n - 1] > w:
            return solve(n - 1, w)
        return max(
            solve(n - 1, w),
            solve(n - 1, w - weight[n - 1]) + values[n - 1],
        )

    print(solve(N, W))
