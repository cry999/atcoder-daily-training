from sortedcontainers import SortedList

N = int(input())
(*X,) = map(int, input().split())
(*C,) = map(int, input().split())

hate = [0] * N
for i in range(N):
    hate[X[i] - 1] += C[i]

hate_with_index = SortedList([(h, i) for i, h in enumerate(hate)])
# print(*hate_with_index)
done = [False] * N

ans = 0
while hate_with_index:
    h, i = hate_with_index.pop(0)
    done[i] = True
    ans += h
    if not done[X[i] - 1]:
        hate_with_index.remove((hate[X[i] - 1], X[i] - 1))
        hate[X[i] - 1] -= C[i]
        hate_with_index.add((hate[X[i] - 1], X[i] - 1))

print(ans)
