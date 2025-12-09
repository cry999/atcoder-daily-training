import os

DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


N, M = map(int, input().split())
*sellers, = sorted(map(int, input().split()))
*buyers, = sorted(map(int, input().split()))

debug(f'{buyers=}')
debug(f'{sellers=}')

lo, hi = 0, max(max(sellers), max(buyers))+1
while hi-lo > 1:
    price = (lo+hi) // 2
    want_to_buy = len([b for b in buyers if b >= price])
    debug(f'At price {price}, want_to_buy={want_to_buy}', end='')

    want_to_sell = len([a for a in sellers if a <= price])
    debug(f', want_to_sell={want_to_sell}')

    if want_to_buy <= want_to_sell:
        hi = price
    else:
        lo = price
print(hi)
