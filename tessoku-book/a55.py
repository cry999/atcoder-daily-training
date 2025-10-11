import bisect

Q = int(input())
cards = []

N = 0
for _ in range(Q):
    q, x = map(int, input().split())
    # print(q, x)
    if q == 1:
        bisect.insort_left(cards, x)
        N += 1
    elif q == 2:
        left = bisect.bisect_left(cards, x)
        right = bisect.bisect_right(cards, x)
        if 0 <= left < N and cards[left] == x:
            cards = cards[:left] + cards[right:]
            N -= (right - left)
    else:
        left = bisect.bisect_left(cards, x)
        if left >= N:
            print(-1)
        else:
            print(cards[left])
    # print('->', cards)
