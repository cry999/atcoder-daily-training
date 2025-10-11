Q = int(input())
scores = {}

for _ in range(Q):
    query = input().split()
    if query[0] == '1':
        scores[query[1]] = query[2]
    else:
        print(scores[query[1]])
