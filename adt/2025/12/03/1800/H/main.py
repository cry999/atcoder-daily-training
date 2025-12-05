N = int(input())

# bit で表せる。
# 例えば 12 を 1011(=12-1=11) に対応づけて、12 のジュースを
# 1, 2, 4 番目の友人に飲ませれば、 S=1011 が返されたら 12 が
# 腐ってるとわかる。

num, b = 0, 1
while b < N:
    num += 1
    b <<= 1
print(num)  # 必要な bit の桁数が犠牲にする友人の数

friends = [[] for _ in range(num)]
for bit in range(N):
    for i in range(num):
        if (bit >> i) & 1:
            friends[i].append(bit+1)

for juices in friends:
    print(len(juices), *juices)

print(int(''.join(reversed(input())), 2)+1)
