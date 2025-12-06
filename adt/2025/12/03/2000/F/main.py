N = int(input())
*A, = map(int, input().split())
*B, = map(int, input().split())

A.sort(reverse=True)
B.sort(reverse=True)


def debug(*args, **kwargs):
    if False:
        print(*args, **kwargs)


buy = 0
box_i = 0
boxed = 0
for i in range(N-1):
    debug(f'[{i=}] {A[i]=} {B[box_i]=} {buy=}')
    if A[i] <= B[box_i]:
        # 箱におもちゃを入れられるので OK
        box_i += 1
        boxed += 1
        continue
    elif buy:
        # すでに箱を買っているので NG
        debug(f'  fail: bought already: {buy=}')
        break
    else:
        # 箱を買う
        debug(f'  buy box for {A[i]=}')
        boxed += 1
        buy = A[i]
else:
    debug(f'[i={N-1}] {A[-1]=} {box_i=} {buy=}')
    if box_i < len(B) and B[box_i] >= A[-1]:
        # 途中で箱を購入したことで、箱が余っているのでそれに入れて成功
        debug(f'  last toy {A[-1]=} into box {B[box_i]=}')
        boxed += 1
    elif not buy:
        debug(f'  last toy {A[-1]=} can buy new box')
        buy = A[-1]
        boxed += 1
        pass
    else:
        debug(f'  last toy {A[-1]=} cannot fit into box {box_i=}')
        # 最後のおもちゃを入れられなかった
        buy = -1
if boxed < N:
    print(-1)
else:
    print(buy)
