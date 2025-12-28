S = input()


# 末尾の 'a' の数と先頭の 'a' の数を計算して、
# 同じ数にしたときに回文になるかを検証する。
head_a, tail_a = 0, 0
for s in S:
    if s == 'a':
        head_a += 1
    else:
        break
for s in S[::-1]:
    if s == 'a':
        tail_a += 1
    else:
        break

if head_a > tail_a:
    # 先頭の 'a' の方が多い場合は操作しても head_a == tail_a
    # にならないので回文にはならない。
    print('No')
else:
    # tail_a - head_a 個の 'a' を末尾から削除する。
    n = len(S) - (tail_a - head_a)
    for i in range(n // 2):
        if S[i] != S[n-i-1]:
            print('No')
            break
    else:
        print('Yes')
