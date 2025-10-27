N = int(input())
*A, = map(int, input().split())
# 1. A の累積和 C をとる
# 2. 最小値を 0 にするために必要な変動を求める
# 3. 2 を C[-1] から引く

C = [0] * (N+1)
for i, a in enumerate(A):
    C[i+1] = C[i] + a

min_c = min(C[1:])
# print(C[-1], min_c)
print(C[-1]-min(0, min_c))
