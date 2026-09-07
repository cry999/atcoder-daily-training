N, Q = map(int, input().split())
(*P,) = map(int, input().split())

index = [0] * (N + 1)
for i in range(N):
    index[P[i]] = i

max_index = N
for _ in range(Q):
    a = int(input())
    index[a] = max_index
    max_index += 1

s = sorted(enumerate(index[1:]), key=lambda x: x[1])
print(*map(lambda x: x[0] + 1, s))
