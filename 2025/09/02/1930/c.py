N = int(input())

names = []
T = 0
for _ in range(N):
    name, n = input().split()
    T += int(n)
    names.append(name)

names.sort()

print(names[T % N])
