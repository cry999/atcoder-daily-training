from heapq import heappop as hpop, heappush as hpush

N = int(input())

queue = []
hpush(queue, (3, 1, 1, 1))

pushed = set()

for _ in range(N - 1):
    n, a, b, c = hpop(queue)
    # print(f"{n=}, {a=}, {b=}, {c=}")

    na = 10 * a + 1
    nb = 10 * b + 1
    nc = 10 * c + 1

    if a <= b <= nc and a + b + nc not in pushed:
        hpush(queue, (a + b + nc, a, b, nc))
        pushed.add(a + b + nc)
    if a <= nb <= c and a + nb + c not in pushed:
        hpush(queue, (a + nb + c, a, nb, c))
        pushed.add(a + nb + c)
    if na <= b <= c and na + b + c not in pushed:
        hpush(queue, (na + b + c, na, b, c))
        pushed.add(na + b + c)

n, _, _, _ = hpop(queue)
print(n)
