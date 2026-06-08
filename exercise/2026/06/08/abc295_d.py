S = input()
N = len(S)


hist = [0] * (1 << 10)
bit = 0
hist[0] = 1
for i, s in enumerate(S):
    n = int(s)
    bit ^= 1 << n
    hist[bit] += 1

print(sum(v * (v - 1) // 2 for v in hist))
