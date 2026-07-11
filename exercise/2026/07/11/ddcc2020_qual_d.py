M = int(input())

S = 0  # 桁和
D = 0  # 桁数
for _ in range(M):
    d, c = map(int, input().split())
    S += d * c
    D += c
print(D - 1 + (S - 1) // 9)
