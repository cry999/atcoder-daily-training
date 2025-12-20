S = input()

i = 0
while i < len(S):
    # 先頭が 'W' までスキップ
    while i < len(S) and S[i] != 'W':
        print(S[i], end='')
        i += 1

    # 'W' の終わりを探す。
    j = i
    while j < len(S) and S[j] == 'W':
        j += 1

    if j < len(S) and S[j] == 'A':
        # 'W'*N + 'A' -> 'A' + 'C'*N
        print('A' + 'C'*(j-i), end='')
        j += 1
    else:
        print('W'*(j-i), end='')

    i = j
print()
