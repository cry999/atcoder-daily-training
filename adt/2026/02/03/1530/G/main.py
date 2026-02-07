from sortedcontainers import SortedList

N, K = map(int, input().split())

# (退店時間, 人数)
in_restaurant = SortedList()

guests = 0
time = 0
for _ in range(N):
    A, B, C = map(int, input().split())
    # すぐに入れないなら退店を待つ
    while guests + C > K:
        # 入れるまで退店を待つ
        exited_time, exited_guests = in_restaurant.pop(0)
        time = max(time, exited_time)
        guests -= exited_guests

    # 入れるようになっている
    time = max(time, A)
    in_restaurant.add((time + B, C))
    guests += C
    print(time)
