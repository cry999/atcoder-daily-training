from sortedcontainers import SortedSet

N, A, B = map(int, input().split())
(*D,) = SortedSet(map(lambda x: int(x) % (A + B), input().split()))
# print(D)
if D[0] + ((A + B) - 1 - D[-1]) >= B:
    print("Yes")
    exit()

for i in range(len(D) - 1):
    if D[i + 1] - D[i] - 1 >= B:
        print("Yes")
        exit()

print("No")
