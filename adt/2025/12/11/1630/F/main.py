N = int(input())
S = input()

i = 0
ans = 0
while i < N:
    # print('skip to 1 or /')
    # '1' or '/' まで移動する
    while i < N and S[i] == '2':
        # print(f'  skip [{i=}]{S[i]=}')
        i += 1

    # '1' の数を数える
    # print('count 1')
    cnt_1 = 0
    while i < N and S[i] == '1':
        # print(f'  count [{i=}]{S[i]=}')
        cnt_1 += 1
        i += 1

    # '1' の後ろは '/' であるはず
    # print('check /')
    if i >= N or S[i] != '/':
        # print(f'  [{i}] not /, continue')
        # そうでないなら、また '1' を探す
        continue
    i += 1

    # '2' の数を数える
    cnt_2 = 0
    # print('count 2')
    while i < N and S[i] == '2':
        # print(f'  count [{i=}]{S[i]=}')
        cnt_2 += 1
        i += 1

    # print(f'  found cnt_1={cnt_1}, cnt_2={cnt_2}')

    ans = max(ans, 2*min(cnt_1, cnt_2)+1)

print(ans)
