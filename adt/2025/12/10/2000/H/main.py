import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N = int(input())
# A[i] の豆の移動可能な距離が C[i]。
*C, = map(int, input().split())
*A, = map(int, input().split())

#  右から左に豆を移動していく。
C.reverse()
C += [0]
A.reverse()
A += [0]

# 一番近い豆の位置に移動すれば良い。
# 一番近い豆の位置までの最短距離を dp で求めれば良い
# 茶碗に入っている豆の数はどうでもいい（一度で移動できる豆の数に制限はないので）

cur = 0
while cur < N-1 and not A[cur]:
    cur += 1

cnt = 0
while cur < N-1:
    debug(f'cur: {cur}')
    next_cur = cur+1
    while next_cur < N-1 and not A[next_cur]:
        next_cur += 1
    debug(f'  next_cur: {next_cur}, N: {N}')

    # cur から next_cur までの最短移動回数を dp で求める。
    dp = [float('inf')] * (next_cur-cur+1)
    dp[0] = 0
    for i in range(next_cur-cur):
        for d in range(1, C[cur+i]+1):
            if i+d > next_cur-cur:
                break
            dp[i+d] = min(dp[i+d], dp[i]+1)

    # 全体の操作回数に cur から next_cur までの最小移動回数を追加する
    # debug(f'  dp: {dp}')
    debug(f'  {cur=} -> {next_cur}: {dp[-1]=}')
    cnt += dp[next_cur-cur]
    # cur を更新しして次に
    cur = next_cur

print(cnt)
