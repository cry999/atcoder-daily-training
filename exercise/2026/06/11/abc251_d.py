W = int(input())

A = []
for n in range(1, 100):
    A.append(n)
    A.append(n * 100)
    A.append(n * 10_000)

A.append(1_000_000)
print(len(A))
print(*A)
