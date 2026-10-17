import sys
import math
import time
import random
from itertools import combinations

N, M, K, T = map(int, input().split())
si, sj = map(int, input().split())
goals = [tuple(map(int, input().split())) for _ in range(M)]


def simulation(
    circles: list[tuple[int, int]],
    gain: int = 1,
    do_print: bool = False,
):
    circles = circles.copy()

    if do_print:
        for a, b in circles:
            print(a, b)

    ci, cj = si, sj
    k = 0
    turn = 0
    while k < M and turn < T:
        gi, gj = goals[k]
        if ci == gi and cj == gj:
            k += 1
            continue

        turn += 1

        # 案2: 現在地と目的地を対角の頂点とする長方形の中にある魔法陣のうち
        # 利用することでゴールに最も近づけるものを使う。

        current_dist = abs(ci - gi) + abs(cj - gj)

        a, b = -1, -1
        best_d = 10**9
        for x, y in circles:
            ni, nj = 2 * x - ci, 2 * y - cj
            d = abs(ni - gi) + abs(nj - gj)
            if 0 <= ni < N and 0 <= nj < N and d + gain < best_d:
                best_d = d
                a, b = x, y

        ni, nj = 2 * a - ci, 2 * b - cj
        next_dist = abs(ni - gi) + abs(nj - gj)
        if 0 <= ni < N and 0 <= nj < N and gain + next_dist < current_dist:
            circles.append((ci, cj))
            circles.remove((a, b))
            if do_print:
                print(f"J {a} {b}")
            ci, cj = ni, nj
            continue

        op = ""
        if ci < gi:
            ci += 1
            op = "D"
        elif ci > gi:
            ci -= 1
            op = "U"
        elif cj < gj:
            cj += 1
            op = "R"
        elif cj > gj:
            cj -= 1
            op = "L"
        if do_print:
            print(op)

    while k < M and (ci, cj) == goals[k]:
        k += 1

    r = abs(ci - goals[k][0]) + abs(cj - goals[k][1]) if k < M else 0

    return (-k, turn, r)


# ゴール間の中点で良いものを探す
candidates = set()
ci, cj = si, sj
for gi, gj in goals:
    candidates.add(((ci + gi) // 2, (cj + gj) // 2))
    ci, cj = gi, gj

for p in range(N * N):
    if len(candidates) >= K:
        break
    candidates.add(divmod(p, N))

ordered_points = sorted(
    (simulation([(ci, cj)], gain=5), ci, cj) for ci, cj in candidates
)
best_score, best_circles = (10**9, 10**9, 10**9), []
top10 = ordered_points[:10]
for circles in combinations(top10, K):
    s = simulation([(ci, cj) for _, ci, cj in circles], gain=5)
    if s < best_score:
        best_score = s
        best_circles = [(ci, cj) for _, ci, cj in circles]

rng = random.Random(0)

current = best_circles.copy()
current_score = simulation(current, gain=5)

evaluated = 0
accepted = 0
improved = 0

# 全目的地に到達できている場合に、手数を焼きなましで削る
if current_score[0] == -M:
    current_cost = current_score[1]

    duration = 1.0  # 焼きなましに使う秒数。全体の制限時間に合わせる
    start = time.perf_counter()

    start_temp = 30.0
    end_temp = 0.5

    while True:
        progress = (time.perf_counter() - start) / duration
        if progress >= 1.0:
            break

        temperature = start_temp * (end_temp / start_temp) ** progress

        # 魔法陣を 1 個選んで動かす
        trial = current.copy()
        index = rng.randrange(K)
        a, b = trial[index]

        radius = max(1, int(12 * (1.0 - progress)))
        na = a + rng.randint(-radius, radius)
        nb = b + rng.randint(-radius, radius)

        if not (0 <= na < N and 0 <= nb < N):
            continue
        if (na, nb) == (a, b):
            continue
        if (na, nb) in trial:
            continue

        trial[index] = (na, nb)
        trial_score = simulation(trial, gain=5)
        evaluated += 1

        # この簡易版では未完走の配置を採用しない
        if trial_score[0] != -M:
            continue

        trial_cost = trial_score[1]
        delta = trial_cost - current_cost

        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            accepted += 1
            current = trial
            current_cost = trial_cost

            # 探索中の現在位置と、過去最高の配置は別に保存する
            if trial_score < best_score:
                improved += 1
                best_score = trial_score
                best_circles = trial.copy()

simulation(best_circles, gain=5, do_print=True)
print(
    f"# evaluated: {evaluated}, accepted: {accepted}, improved: {improved}",
    file=sys.stderr,
)
