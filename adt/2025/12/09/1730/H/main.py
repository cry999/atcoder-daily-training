import os
import sys
from collections import defaultdict


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


def all_lines(N: int) -> int:
    """
    回文にするために比較するペアの数
    = sum(選択した部分列に含まれる線の個数 x 部分列の選択の仕方)
    = sum((N+1-i) * (i//2) for i in range(1, N+1))  # i: 部分列の長さ

    これを数学的に整理すると m = N//2 として
    (2N+1)m(m+1)/2 - 2m(m+1)(2m+1)/3
    """
    m = N//2
    return (2*N+1)*m*(m+1)//2 - 2*m*(m+1)*(2*m+1)//3


N = int(input())
*A, = map(int, input().split())

# 「良い線」を数える。

positions = defaultdict(list)

for i, a in enumerate(A):
    positions[a].append(i)

good_lines = 0

for pos_list in positions.values():
    lo, hi = 0, len(pos_list)-1
    while lo < hi:
        if pos_list[lo] < N-pos_list[hi]:
            good_lines += (pos_list[lo]+1) * (hi-lo)
            lo += 1
        else:
            good_lines += (N-pos_list[hi])*(hi-lo)
            hi -= 1

ans = all_lines(N) - good_lines
print(ans)
