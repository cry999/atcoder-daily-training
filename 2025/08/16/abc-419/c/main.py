N = int(input())

people = []

for _ in range(N):
    i, j = map(int, input().split(' '))
    people.append((i, j))

max_i, min_j = max(people, key=lambda x: x[0])[0], \
    min(people, key=lambda x: x[0])[0]
mid_i = (max_i + min_j) // 2
max_j, min_j = max(people, key=lambda x: x[1])[1], \
    min(people, key=lambda x: x[1])[1]
mid_j = (max_j + min_j) // 2

max_dist_i = max(abs(i - mid_i) for i, j in people)
max_dist_j = max(abs(j - mid_j) for i, j in people)

ans = max(max_dist_i, max_dist_j)

print(ans)
