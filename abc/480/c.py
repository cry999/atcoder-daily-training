import math

N, K, T = map(int, input().split())
(*A,) = map(int, input().split())
A.sort()

t = 0  # 水が止まる時刻
ans = 0  # ボタンを押した回数
for a in A:
    a = min(a, T)
    if a <= t:
        # aoki が水が出ている間に押してくれるなら延長
        t = a + K
    else:
        # aoki がボタンを押してくれるのは a なので、それまでボタンを押し続けないといけない
        ans += math.ceil((a - t) / K)
        t = a + K

if t < T:
    ans += math.ceil((T - t) / K)

print(ans)
