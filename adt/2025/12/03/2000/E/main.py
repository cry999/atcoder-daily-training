N = int(input())

s = set()
for _ in range(N):
    S = input()
    s.add(hash(min(S, S[::-1])))

print(len(s))
