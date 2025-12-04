N, M = map(int, input().split())

totals = {}
for _ in range(N):
    A, B = map(int, input().split())
    if A not in totals:
        size, num = 0, 0
    else:
        size, num = totals[A]
    totals[A] = (size+B, num+1)

for i in range(1, M+1):
    size, num = totals.get(i, (0, 1))
    print(f'{size/num:.10f}')
