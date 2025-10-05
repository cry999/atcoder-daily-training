from functools import reduce as r

N = int(input())
print('First' if r(lambda x, y: x ^ y, map(int, input().split()), 0) != 0 else 'Second')
