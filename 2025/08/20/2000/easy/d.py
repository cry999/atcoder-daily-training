N, D = map(int, input().split())

snakes = []
for i in range(N):
    snakes.append(list(map(int, input().split())))

for k in range(1, D+1):
    heavy = max(map(lambda x: x[0] * (x[1]+k), snakes))
    print(heavy)
