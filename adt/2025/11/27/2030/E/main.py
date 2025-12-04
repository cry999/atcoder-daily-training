import collections

N = int(input())
S = input()

# b_pos[i] = i 番目の 'B' の位置
b_pos = [-1] * N
p = 0
for i, s in enumerate(S):
    if s == 'B':
        b_pos[p] = i
        p += 1

# op_a: 'A' でスタートするように操作した場合の操作回数
# op_b: 'B' でスタートするように操作した場合の操作回数
op_a, op_b = 0, 0
