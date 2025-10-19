N, K = map(int, input().split())
S = input()

m = {}

for i in range(N-K+1):
    s = S[i:i+K]
    m[s] = m.get(s, 0)+1

x = max(m.values())

print(x)
print(*sorted(k for k, v in m.items() if v == x))
