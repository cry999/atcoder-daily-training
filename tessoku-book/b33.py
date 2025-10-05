from functools import reduce as r

N, H, W = map(int, input().split())
# 縦方向・横方向の移動をそれぞれ Nim の山と捉えられる。
# したがって、Nim の定理より、Xor 和が 0 でないとき先手必勝、0 のとき後手必勝。
AB = [tuple(map(int, input().split())) for _ in range(N)]
print(r(
    lambda x, y: x ^ y,
    ((a-1) ^ (b-1) for a, b in AB),
    0,
) != 0 and 'First' or 'Second')
