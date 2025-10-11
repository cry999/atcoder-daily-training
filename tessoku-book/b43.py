# 減点法で考える

N, M = map(int, input().split())
scores = [M] * N

for A in map(int, input().split()):
    scores[A-1] -= 1

for score in scores:
    print(score)
