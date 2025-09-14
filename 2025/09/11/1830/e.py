import bisect

Q = int(input())
S = []
cnt = dict()

for _ in range(Q):
    command, *args = map(int, input().split())
    if command == 1:
        x = args[0]
        if bisect.bisect_left(S, x) == bisect.bisect_right(S, x):
            bisect.insort_left(S, x)
        cnt[x] = cnt.get(x, 0) + 1
    elif command == 2:
        x, c = args
        cnt[x] = max(0, cnt.get(x, 0) - c)
    else:
        while S and cnt.get(S[0], 0) == 0:
            S.pop(0)
        while S and cnt.get(S[-1], 0) == 0:
            S.pop(-1)
        print(S[-1] - S[0] if S else 0)
