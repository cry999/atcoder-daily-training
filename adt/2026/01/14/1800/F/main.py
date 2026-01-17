N, D, P = map(int, input().split())
(*F,) = map(int, input().split())

F.sort(reverse=True)
chunk = []
i = 0
while i < N:
    chunk.append(sum(F[i : i + D]))
    i += D

cost = 0
for c in chunk:
    if c > P:
        cost += P
    else:
        cost += c
print(cost)
