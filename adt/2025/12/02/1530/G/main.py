N = int(input())
S = [c for c in input()]
Q = int(input())

# 大文字・小文字の入れ替えは最後の操作だけ知っていれば良い
queries = []
last_toggle_index = 0
last_toggle_query = -1
for i in range(Q):
    t, x, c = input().split()
    queries.append((int(t), int(x), c))
    if t == '2':
        last_toggle_query = 2
        last_toggle_index = i
    if t == '3':
        last_toggle_query = 3
        last_toggle_index = i

# 初期は全部入れ替える
if last_toggle_query == 2:
    S = [c.lower() for c in S]
elif last_toggle_query == 3:
    S = [c.upper() for c in S]

for i, (t, x, c) in enumerate(queries):
    if t != 1:
        continue
    if i < last_toggle_index:
        # 最後の入れ替え操作に合わせてそれより前の置換は
        # 入れ替えを適用した文字を利用する
        if last_toggle_query == 2:
            S[x-1] = c.lower()
        if last_toggle_query == 3:
            S[x-1] = c.upper()
    else:
        S[x-1] = c

print(''.join(S))
