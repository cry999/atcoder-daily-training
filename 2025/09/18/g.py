N = int(input())
S = input()

T = [''] * (len(S))
i = 0
starts = []
for c in S:
    # print(c, i, len(T))
    if c == ')':
        if starts:
            i = starts.pop()  # '(' まで戻る
        else:  # 対応する '(' がないので、文字列として処理
            T[i] = c
            i += 1
    elif c == '(':
        starts.append(i)  # '(' の位置を記録
        T[i] = c
        i += 1
    else:  # 進む
        T[i] = c
        i += 1

print(''.join(T[:i]))
