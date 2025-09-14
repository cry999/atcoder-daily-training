import heapq


def debug(*args):
    # print(*args)
    pass


N, K = map(int, input().split())

# inner: 店内イベント
inner = []
# count: 店内の人数
count = 0
now = 0

for _ in range(N):
    # A: 待ち始め時間, B: 店内時間, C: 人数
    A, B, C = map(int, input().split())
    debug('---')
    debug('[ now ] now', now, 'count', count, 'inner', inner)
    debug('[ reserve ] event @', A, '/ duration:', B, '/ member:', C)

    if count + C <= K:  # 即時入店可能
        count += C
        now = max(now, A)
        debug('[ no wait ]')
        debug('[ in ] from', now, 'to', now + B, 'member', C)
        heapq.heappush(inner, (now + B, C))  # 退店イベント
        print(now)
    else:  # 退店まち
        debug('[ wait ]', now, count, inner)
        while count + C > K:
            leave_time, leave_count = heapq.heappop(inner)
            count -= leave_count
            now = max(now, leave_time)
            debug('[ -> leave ]', leave_time, leave_count, now, count, inner)
        debug('[ in ] from', now, 'to', now + B, 'member', C)
        now = max(now, A)
        count += C
        heapq.heappush(inner, (now + B, C))  # 退店イベント
        print(now)

    debug('[ now ] now', now, 'count', count, 'inner', inner)
