T = int(input())

for _ in range(T):
    N, W = map(int, input().split())
    (*C,) = map(int, input().split())

    sum_by_mod = [0] * (2 * W)
    for i, c in enumerate(C):
        sum_by_mod[(i + 1) % (2 * W)] += c

    sum_to_w = sum(sum_by_mod[:W])
    ans = sum_to_w
    for x in range(2 * W):
        sum_to_w -= sum_by_mod[(x) % (2 * W)]
        sum_to_w += sum_by_mod[(x + W) % (2 * W)]
        ans = min(ans, sum_to_w)
    print(ans)
