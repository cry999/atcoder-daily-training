N, W = map(int, input().split())
events = []
for _ in range(N):
    s, t, p = map(int, input().split())
    events.append((s, p))
    events.append((t, -p))

events.sort()

total = 0
last_time = 0
for t, p in events:
    if last_time != t:
        if total > W:
            print("No")
            break
    total += p
else:
    print("Yes")
