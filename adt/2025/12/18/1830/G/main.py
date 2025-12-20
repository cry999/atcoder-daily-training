N, M = map(int, input().split())
*X, = map(int, input().split())

# 家と家の間のカバーされていない空間を最大化する。
# M-1 個の空間をカバーしなくて良いので、X の差分を
# 大きい順に M-1 小鳥除く。
# あとは、残りのカバーしないといけない範囲の総和
# が答えになる。

X.sort()
*D, = sorted(X[i+1]-X[i] for i in range(N-1))
print(sum(D[:-(M-1)] if M-1 else D))
