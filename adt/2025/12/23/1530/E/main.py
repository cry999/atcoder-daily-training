N = int(input())

dup = set()
max_score, max_i = -1, -1

for i in range(N):
    s, t = input().split()

    if s in dup:
        continue
    dup.add(s)
    score = int(t)
    if score > max_score:
        max_score = score
        max_i = i + 1

print(max_i)
