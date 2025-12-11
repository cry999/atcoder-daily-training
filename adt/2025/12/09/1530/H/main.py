import bisect
import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


X = int(input())

# 差が 0 でない等差数を全部作る。
numbers = [i+1 for i in range(9)]
for d in range(1, 10):
    for i in range(1, 10):
        # 差が d の等差数
        j, k = i, i
        while k+d <= 9:
            k += d
            j = 10*j + k
            numbers.append(j)
        # 差が -d の等差数
        j, k = i, i
        while k-d >= 0:
            k -= d
            j = 10*j + k
            numbers.append(j)


# 差が 0 の等差数は無限にあるが、X 以上で最小のものの候補は、
# 「X と桁数が同じ or 一つ多い All-1」なので、それらを追加する。
digit = len(str(X))
for i in range(1, 10):
    numbers.append(sum(i*10**j for j in range(digit)))
numbers.append(sum(i*10**j for j in range(digit+1)))

numbers.sort()
debug(numbers)

i = bisect.bisect_left(numbers, X)
print(numbers[i] if i < len(numbers) else -1)
