N, M, C = map(int, input().split())
A = sorted(map(int, input().split()))
B = sorted(map(int, input().split()))

i, j = 0, 0
assigned = 0
while i < N and j < M:
    if A[i] >= B[j]:
        assigned += 1
        j += 1

    i += 1

print(assigned * C)
