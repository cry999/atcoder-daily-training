# ブルートフォースで行く
# a, b, c を単調増加とする(a <= b <= c)
# 各組み合わせに対して、a, b, c を入れ替えたパターンを計算して
# 総数を計算する。

S, T = map(int, input().split())

count = 0

for a in range(S + 1):
    for b in range(a, S + 1):
        for c in range(b, S + 1):
            if a + b + c <= S and a * b * c <= T:
                # print(a, b, c)
                if a == b == c:  # 全て同じ
                    count += 1
                elif a == b or b == c or a == c:  # 2つ同じ
                    count += 3
                else:  # 全て異なる
                    count += 6

print(count)
