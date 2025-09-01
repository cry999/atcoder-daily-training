# O(N) で解く

S = input()
T = input()

m = {}
for c in S:
    m[c] = m.get(c, 0) + 1

for c in T:
    # @ は、あとで S の残った文字と突合する
    if c == '@':
        continue

    rest = m.get(c, 0)
    # まずは同じ文字を消費
    if rest != 0:
        m[c] = rest - 1
        continue
    # 次に @ を消費
    if c in 'atcoder' and m.get('@', 0) > 0:
        m['@'] -= 1
        continue

    # それ以外は NG
    print('No')
    exit()

# S に残った文字を T の @ で処理できるかチェック
for c in m.keys():
    # 残っていないなら OK
    if m[c] == 0:
        continue
    # @atcoder の文字なら T の @ で処理できる
    if c in '@atcoder':
        continue

    # それ以外の文字が残っているなら NG
    print('No')
    exit()

print('Yes')
