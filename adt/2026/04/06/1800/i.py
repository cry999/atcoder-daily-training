T = int(input())

for _ in range(T):
    N, M = map(int, input().split())
    A = sorted(map(int, input().split()), reverse=True)
    sum_a = sum(A)
    K = (N + M + 1) // 2

    lengths = set()
    for a in A:
        lengths.add(a)
        while a:
            lengths.add(a // 2)
            lengths.add(a - a // 2)
            a //= 2
    lengths = sorted(lengths, reverse=True)

    lo, hi = 0, A[0] + 1

    while hi - lo > 1:
        mi = (hi + lo) // 2

        counts = {}
        for a in A:
            counts[a] = counts.get(a, 0) + 1

        for a in lengths:
            if a < 2 * mi - 1:
                break
            cnt = counts.get(a, 0)
            if cnt == 0:
                continue

            del counts[a]
            counts[a // 2] = counts.get(a // 2, 0) + cnt
            counts[a - a // 2] = counts.get(a - a // 2, 0) + cnt

        num_ge = sum(cnt for a, cnt in counts.items() if a >= mi)
        if num_ge < K:
            hi = mi
            continue

        need = K
        s = 0
        for a, cnt in sorted(counts.items()):
            if a < mi:
                continue
            take = min(need, cnt)
            s += take * a
            need -= take
            if need == 0:
                break

        if s + (N + M - 1) // 2 <= sum_a:
            lo = mi
        else:
            hi = mi

    print(lo)
