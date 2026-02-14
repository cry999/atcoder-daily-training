N = int(input())
S = [input() for _ in range(N)]

m = max(len(s) for s in S)
for s in S:
    t = (m - len(s)) // 2
    print("." * t + s + "." * t)
