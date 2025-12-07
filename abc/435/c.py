N = int(input())
*A, = map(int, input().split())

i = 1
r = A[0]-1
while i < N and r:
    # print('i=', i, r, end='')
    r = max(r, A[i]) - 1
    # print(' -> ', r)
    i += 1

print(i)
