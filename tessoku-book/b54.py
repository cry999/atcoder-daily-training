N = int(input())
m = {}

for _ in range(N):
    A = input()
    m[A] = m.get(A, 0) + 1

print(sum(v * (v-1) // 2 for v in m.values() if v > 1))
