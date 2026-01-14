# 2 進数使うともうちょっと速くなりそう？
from collections import defaultdict
from heapq import heappop as hpop, heappush as hpush

N = int(input())
slimes = defaultdict(int)

queue = []
pushed = set()

total_slimes = 0
for _ in range(N):
    size, num = map(int, input().split())
    slimes[size] += num
    total_slimes += num
    hpush(queue, size)
    pushed.add(size)

while queue:
    size = hpop(queue)
    if slimes[size] < 2:
        continue

    total_slimes -= slimes[size] // 2
    double_size = size * 2
    double_size_num = slimes[size] // 2
    slimes[size] %= 2
    slimes[double_size] += double_size_num

    if double_size not in pushed:
        hpush(queue, double_size)
        # 同じサイズが存在しないことが保証されているので、
        # 最初に提示されたサイズ以外は重複チェック対象外
        # pushed.add(double_size)

print(total_slimes)
