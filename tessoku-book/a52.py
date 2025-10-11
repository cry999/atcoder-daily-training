Q = int(input())
queue = []
for _ in range(Q):
    query = input().split()
    if query[0] == '1':
        queue.append(query[1])
    elif query[0] == '2':
        print(queue[0])
    else:
        queue = queue[1:]
