N = int(input())

S = []
for _ in range(N):
    S.append(input())

while len(S) > 0:
    s = S.pop()
    print(s)
