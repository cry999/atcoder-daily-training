N, X = map(int, input().split())
A = list(input())
queue = [X-1]
A[X-1] = '@'

while queue:
    pos, queue = queue[0], queue[1:]
    if pos-1 >= 0 and A[pos-1] == '.':
        A[pos-1] = '@'
        queue.append(pos-1)
    if pos+1 < N and A[pos+1] == '.':
        A[pos+1] = '@'
        queue.append(pos+1)
    # print(''.join(A))

print(''.join(A))
