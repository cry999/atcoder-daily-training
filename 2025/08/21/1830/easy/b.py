N, c1, c2 = input().split()
N = int(N)

S = input()

for s in S:
    print(c2 if s != c1 else s, end='')
print()
