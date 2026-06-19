N, C = map(int, input().split())

events = []
for _ in range(N):
    a, b, c = map(int, input().split())
    events.append((a, c))
    events.append((b + 1, -c))
events.sort()

ans = 0
pay = 0
last_day = events[0][0]
for day, price in events:
    if day != last_day:
        ans += min(pay, C) * (day - last_day)
        last_day = day

    pay += price

print(ans)
