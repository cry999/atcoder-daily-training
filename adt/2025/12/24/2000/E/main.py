N = int(input())
S = input()
Q = int(input())

conv = {chr(ord("a") + i): chr(ord("a") + i) for i in range(26)}

for _ in range(Q):
    c, d = input().split()
    for k, v in conv.items():
        if v == c:
            conv[k] = d

print("".join(conv[s] for s in S))
