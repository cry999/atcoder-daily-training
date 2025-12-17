N = int(input())
S = input()

ans = 0
for s in [S, S[::-1]]:
    i = 0
    while i < N:
        # '-' はスキップ
        while i < N and s[i] == '-':
            i += 1

        # n: 団子(o)の数
        n = 0
        while i < N and s[i] == 'o':
            i += 1
            n += 1

        # 最後に '-' がつく場合のみ正しい。
        if i < N:
            ans = max(ans, n)

print(ans if ans else -1)
