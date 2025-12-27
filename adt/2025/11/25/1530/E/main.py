import bisect

T = int(input())

for _ in range(T):
    N = int(input())
    *S, = map(int, input().split())
    s1, sn = S[0], S[-1]
    if len(S) <= 2:
        if 2*s1 >= sn:
            print(2)
        else:
            print(-1)
        continue

    s = sorted(S[1:-1])
    lo = -1
    cnt = 2
    while s1*2 < sn:
        prev = lo
        lo = bisect.bisect_left(s, 2*s1, lo=lo+1)
        # print(f'  before: {s1=}, {lo=}, {sn=}, {cnt=}')
        if lo < len(s) and s[lo] != 2*s1:
            lo -= 1
        if lo == len(s):
            if lo-1 == prev or s[lo-1]*2 < sn:
                cnt = -1
            else:
                cnt += 1
            break
        # print(f'  after : {s1=}, {lo=}, {sn=}, {cnt=}')
        if prev == lo:
            cnt = -1
            break
        s1 = s[lo]
        cnt += 1
    print(cnt)
