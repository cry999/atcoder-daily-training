import bisect

Q = int(input())

cards = []

N = 0
for _ in range(Q):
    q, x = map(int, input().split())
    if q == 1:
        N += 1
        bisect.insort_left(cards, x)
    else:
        if N == 0:
            print(-1)
            continue
        ans = float('inf')
        left = bisect.bisect_left(cards, x)
        if 0 <= left < N:
            ans = min(ans, abs(cards[left] - x))
        if left > 0:
            ans = min(ans, abs(cards[left-1] - x))
        right = bisect.bisect_right(cards, x)
        if 0 <= right < N:
            ans = min(ans, abs(cards[right] - x))
        if right < N-1:
            ans = min(ans, abs(cards[right+1] - x))
        print(ans)
