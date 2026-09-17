# >>> atcoder-stat >>>
# started_at  = 2026-09-17T16:23:46+09:00
# solved_at   = 2026-09-17T16:50:23+09:00
# duration_ms = 1597390
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N = int(input())
events = [tuple(map(int, input().split())) for _ in range(N)]

# enemies[x]: 出現済み && 倒していないタイプ x のモンスターの数
enemies = [0] * (N + 1)
# num_potions[i]: i 番目のイベントで持っているポーションの数
num_potions = [0] * (N + 1)
# get_potion[i]: i 番目のポーションイベントでポーションを手に入れるかどうか
get_potion = []
for i in range(N - 1, -1, -1):
    t, x = events[i]
    if t == 1:
        # 敵がこのあと出現するなら持っておく。
        if enemies[x] > 0:
            enemies[x] -= 1
            num_potions[i + 1] += 1
            get_potion.append(1)
        else:
            get_potion.append(0)
    else:  # t == 2
        num_potions[i + 1] -= 1
        enemies[x] += 1

if any(e > 0 for e in enemies):
    # 敵が残っている
    print(-1)
else:
    for i in range(N):
        num_potions[i + 1] += num_potions[i]
    print(max(num_potions))
    print(*reversed(get_potion))
