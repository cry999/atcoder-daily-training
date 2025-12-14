import math
import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


def prec(n: float) -> float:
    d = int(n * 1e15) / 1e15
    # debug('  prec:', d)
    if d < 0:
        return 0.0
    return d


def dist(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


T = int(input())

x, y = 0, 1

for t in range(T):
    # debug(f'Case #{t+1}:')
    TSx, TSy, TGx, TGy = map(int, input().split())
    ASx, ASy, AGx, AGy = map(int, input().split())

    TD, AD = dist(TSx, TSy, TGx, TGy), dist(ASx, ASy, AGx, AGy)
    if TD > AD:
        TD, AD = AD, TD
        TS, TG = (ASx, ASy), (AGx, AGy)
        AS, AG = (TSx, TSy), (TGx, TGy)
    else:
        TS, TG = (TSx, TSy), (TGx, TGy)
        AS, AG = (ASx, ASy), (AGx, AGy)

    # debug(f'  TD: {TD}, AD: {AD}')

    a1 = 0
    a1 += ((TG[x]-TS[x]) / TD - (AG[x]-AS[x]) / AD)**2
    a1 += ((TG[y]-TS[y]) / TD - (AG[y]-AS[y]) / AD)**2

    b1 = 0
    b1 += 2*((TG[x]-TS[x])/TD - (AG[x]-AS[x])/AD)*(TS[x]-AS[x])
    b1 += 2*((TG[y]-TS[y])/TD - (AG[y]-AS[y])/AD)*(TS[y]-AS[y])

    c1 = (TS[x]-AS[x])**2 + (TS[y]-AS[y])**2

    # debug(f'  a: {a1}, b: {b1}, c: {c1} / {(-b1/(2*a1) if a1 else 'inf')}')

    def f1(x: float) -> float:
        return a1*x**2 + b1*x + c1

    ans = min(f1(0), f1(TD))
    # debug(f'  f1(0): {f1(0)}')
    # debug(f'  f1(TD): {f1(TD)}')
    if abs(a1) > 1e-15 and 0 <= -b1/(2*a1) <= TD:
        # debug(f'  f1({-b1/2*a1=}): {f1(-b1/(2*a1))}')
        ans = min(ans, f1(-b1/(2*a1)))

    a2 = 1

    b2 = 0
    b2 += 2*(AG[x]-AS[x])*(AS[x]-TG[x])
    b2 += 2*(AG[y]-AS[y])*(AS[y]-TG[y])
    b2 /= AD

    c2 = (AS[x]-TG[x])**2 + (AS[y]-TG[y])**2

    def f2(x: float) -> float:
        return a2*x**2 + b2*x + c2

    # debug(f'  a: {a2}, b: {b2}, c: {c2} / {(-b2/(2*a2) if a2 else "inf")}')
    # debug(f'  f2({TD=}): {f2(TD)}')
    # debug(f'  f2({AD=}): {f2(AD)}')

    ans = min(ans, f2(TD), f2(AD))
    if abs(a2) > 1e-15 and TD <= -b2/(2*a2) <= AD:
        # debug(f'  f2({-b2/2*a2=}): {f2(-b2/(2*a2))}')
        ans = min(ans, f2(-b2/(2*a2)))

    print(math.sqrt(prec(ans)))
