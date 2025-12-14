N, K = map(int, input().split())
*A, = map(lambda x: int(x)-K, input().split())
# A[i]-K を考えることで、「平均が K 以下」は「合計が 0 以下」
# に置き換えられる。

# B[i] := -(A[0] + ... A[i-1])
# マイナスの累積和とすることで、sum(A[i]-K, L-1, R) >= 0 の条件が
# B[L-1] <= B[R] となり、最長増加部分列っぽく扱える。
B = [0] * (N+1)
for i in range(N):
    B[i+1] = B[i] - A[i]

# q: L の候補を単調減少列として管理する。
# WHY: 仮に B[i] <= B[i+1] <= B[R] であるとする。
# この場合、R に対する L-1 として i+1 も i も選択可能であるが、
# 求めるのが最大の R-(L-1) であることを考えると i+1 を選択することは考えなくて良い。
# 結局上記を満たす i+1 を利用することはないため、単調減少列で良い。
q = [(float('inf'), -1)]
max_len = 0
for i in range(N+1):
    if q[-1][0] > B[i]:
        q.append((B[i], i))

    lo, hi = 0, len(q)
    while hi-lo > 1:
        mi = (lo+hi)//2
        if q[mi][0] <= B[i]:
            hi = mi
        else:
            lo = mi
    # print(f'{i=}, {hi=}, {q[hi]=}')
    max_len = max(max_len, i-q[hi][1])
    # print(hi)
print(max_len)
