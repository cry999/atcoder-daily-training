from collections import defaultdict
import bisect


W, H = map(int, input().split())

N = int(input())
strawberries = [tuple(map(int, input().split())) for _ in range(N)]
strawberries.sort()

A = int(input())
*X, = map(int, input().split())
X.append(W)
B = int(input())
*Y, = map(int, input().split())
Y.append(H)

# どのいちごが同じ区域に入るかを考える。
# いちごを中心に、仕切りの位置を考える。


# 800ms
groups = []

xi = 0
si = 0
while xi <= A and si < N:
    if strawberries[si][0] > X[xi]:
        xi += 1
        continue
    sl, sr = si, si
    while sr+1 < N and strawberries[sr+1][0] < X[xi]:
        sr += 1
    # print(f'{xi=}: {sl=}, {sr=}')

    si = sr+1
    xi += 1
    if sr-sl+1 == 1:
        groups.append(1)
        continue
    # x 軸で同じ区域に入るのが複数ある場合は、
    # y 軸も確認する。
    hist = defaultdict(int)
    for i in range(sl, sr+1):
        # print(f'  {i=}: {strawberries[i]=}')
        yi = bisect.bisect_left(Y, strawberries[i][1])
        hist[yi] += 1

    for v in hist.values():
        groups.append(v)

# print(f'{groups=}')
max_val = max(groups)
min_val = min(groups)
if len(groups) < (A+1)*(B+1):
    # 部屋の数より group の数が少ない場合、0 の部屋が必ずある
    min_val = 0
print(min_val, max_val)


# 以下が模範回答: 800ms
# memo = defaultdict(int)
# for p, q in strawberries:
#     xi = bisect.bisect_left(X, p)
#     yi = bisect.bisect_left(Y, q)
#     memo[(xi, yi)] += 1
#
# min_val = min(memo.values()) if len(memo) >= (A+1)*(B+1) else 0
# max_val = max(memo.values())
#
# print(min_val, max_val)
