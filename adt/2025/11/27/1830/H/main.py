from collections import defaultdict


N, M = map(int, input().split())
*S, = map(int, input().split())  # N-1
*X, = map(int, input().split())  # M

# A のいずれかの値が決まれば、A は一意に決まる。
# つまり、A[i] の値が X になるときの A[0] は一意。
# したがって、A[i] がラッキーナンバーになる時の A[0]
# を計算して、A[0] ごとにラッキーナンバーの数をカウント
# すれば良い。

# A[i] = S[i] - S[i-1] + S[i-2] - ... + (-1)^{i-1}S[1] + (-1)^{i}A[0]
# であり、S[i] - S[i-1] + ... + (-1)^{i-1} S[1] の部分は固定であるので
# 先に計算しておく。
offsets = [0] * N
for i in range(N-1):
    offsets[i+1] = S[i] - offsets[i]

a1_map = defaultdict(int)
for i in range(N):
    for x in X:
        a1 = ((-1) ** (i % 2))*(x-offsets[i])
        a1_map[a1] += 1

print(max(a1_map.values()))

# for a1, cnt in a1_map.items():
#     print(a1, cnt)
