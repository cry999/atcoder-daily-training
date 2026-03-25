N = int(input())

tank = 0
prev_t = 0
for _ in range(N):
    t, v = map(int, input().split())
    tank = max(0, tank - (t - prev_t)) + v
    # print(tank)

    prev_t = t

print(tank)
