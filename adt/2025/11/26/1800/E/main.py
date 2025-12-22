N, K = map(int, input().split())
drags = [tuple(map(int, input().split())) for _ in range(N)]
drags.sort()

num_daily = sum(map(lambda x: x[1], drags))
if num_daily <= K:
    print(1)
    exit()

for day, num in drags:
    num_daily -= num
    if num_daily <= K:
        print(day+1)
        break
