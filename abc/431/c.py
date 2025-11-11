import bisect


N, M, K = map(int, input().split())
*H, = map(int, input().split())
*W, = map(int, input().split())

H.sort()
W.sort()

idx = 0
for h in H[:K]:
    tmp = bisect.bisect_left(W, h, lo=idx)
    if tmp == M:
        print('No')
        break
    idx = tmp+1
else:
    print('Yes')
