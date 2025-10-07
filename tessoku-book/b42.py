N = int(input())

pp, pm, mp, mm = 0, 0, 0, 0
for _ in range(N):
    A, B = map(int, input().split())
    if A+B > 0:
        pp += A+B
    if A-B > 0:
        pm += A-B
    if -A+B > 0:
        mp += -A+B
    if -A-B > 0:
        mm += -A-B
print(max(pp, pm, mp, mm))
