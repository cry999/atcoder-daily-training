N = int(input())
cl = []
for _ in range(N):
    c, length = input().split()
    length = int(length)
    cl.append((c, length))

if sum(map(lambda x: x[1], cl)) > 100:
    print('Too Long')
else:
    print(''.join(map(lambda x: x[0]*x[1], cl)))
