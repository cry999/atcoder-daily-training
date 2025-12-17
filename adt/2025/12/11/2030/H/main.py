import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N, C = map(int, input().split())


# or 0 / and 1 / xor 0 は素通りなので無視。
# 最後に出た or 1 / and 0 は必ず 1 か 0 にするので大事。
# xor 1 が奇数個出たら ↑ を反転。偶数個ならそのまま出す。

# O(N logC) で解ける。


# bit[i] := C の i ビット目
bit = [0]*30
c, i = C, 0
while c:
    bit[i] = c & 1
    c >>= 1
    i += 1

debug(f'{C=}, {bit=}')
# xor 1 の個数
xor_cnt = [0]*30
# or 1 / and 0 で確定していないビットは毎回 xor を作用させないといけない。
pre_xor = [True]*30
for _ in range(N):
    T, A = map(int, input().split())
    debug(f'=== {T=}, {A=} ===')
    for i in range(len(bit)):
        b = bit[i]
        if pre_xor[i]:
            bit[i] = b ^ xor_cnt[i]

    if T == 1:  # and
        debug('  AND operation')
        for i in range(30):
            if A & (1 << i) == 0:
                bit[i] = 0
                xor_cnt[i] = 0
                pre_xor[i] = False
    elif T == 2:  # or
        debug('  OR operation')
        for i in range(30):
            if A & (1 << i) != 0:
                bit[i] = 1
                xor_cnt[i] = 0
                pre_xor[i] = False
    else:  # xor
        debug('  XOR operation')
        for i in range(30):
            if A & (1 << i) != 0:
                # 0 or 1 だけ知っていれば良い。
                bit[i] ^= 1
                xor_cnt[i] = 1-xor_cnt[i]

    # debug(f'  {bit=}')
    # debug(f'  {xor_cnt=}')
    ans = 0
    for i in range(len(bit)):
        b = bit[i]
        ans |= (b << i)
    debug(f'  {ans=}')
    print(ans)
