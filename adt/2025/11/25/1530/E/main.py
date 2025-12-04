import bisect


T = int(input())
for _ in range(T):
    N = int(input())
    *S, = map(int, input().split())

    S1, SN = S[0], S[-1]
    S.sort()
    n = S.index(SN)

    last, last_i, cnt = S1, 0, 1
    while last != SN:
        i = bisect.bisect_left(S, last*2, lo=last_i, hi=n)
        # print(f'{last=} {i=}')
        if i >= len(S):
            cnt += 1
            break
        elif S[i] > 2*last:
            if i-1 == last_i:
                cnt = -1
                break
            else:
                last, last_i = S[i-1], S[i]
                cnt += 1
        else:  # S[i] <= 2*last
            last, last_i = S[i], i
            cnt += 1

        # print(f'{last_i=}')

    print(cnt)
