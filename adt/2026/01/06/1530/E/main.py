# 右端から操作するので簡単のために反転する
S = input()[::-1]

op_a = 0
ans = 0
i = 0
for s in S:
    n = (int(s) - op_a) % 10
    op_a += n
    op_a %= 10
    ans += n + 1  # 1 は末尾追加操作分

print(ans)
