N = int(input())
S = input()

g = [0] * N
g[0] = 1

last_a = -1
for i, c in enumerate(S):
    if c == 'A':
        g[i+1] = g[i] + 1
        last_a = i
    elif c == 'B':
        # B の右端でないなら一旦スルー
        if i+1 != N-1 and S[i+1] == 'B':
            continue
        # B の右端にきたら、最後に見つけた左の A まで戻りながら
        # 高さを再計算する
        g[i+1] = 1
        for j in range(i, last_a, -1):
            g[j] = max(g[j], g[j+1]+1)
# print(*g)
print(sum(g))
