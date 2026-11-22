# >>> atcoder-stat >>>
# started_at  = 2026-11-19T17:48:40+09:00
# solved_at   = 2026-11-19T18:06:15+09:00
# duration_ms = 1055809
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
first_choice = [0] * (N + 1)
second_choice: list[dict[int, int]] = [{} for _ in range(N + 1)]
for _ in range(M):
    a, b = map(int, input().split())
    first_choice[a] += 1
    second_choice[a][b] = second_choice[a].get(b, 0) + 1

max1_i, max1_v = -1, -1
max2_i, max2_v = -1, -1
for i, v in enumerate(first_choice):
    if i == 0:
        continue
    if v > max1_v:
        max2_i, max2_v = max1_i, max1_v
        max1_i, max1_v = i, v
    elif v > max2_v:
        max2_i, max2_v = i, v

for i in range(1, N + 1):
    ans_i, ans_v = max1_i, max1_v
    if i == max1_i:
        ans_i, ans_v = max2_i, max2_v

    for b, v in second_choice[i].items():
        cand_i, cand_v = b, first_choice[b] + v
        if cand_v > ans_v or cand_v == ans_v and cand_i < ans_i:
            ans_i, ans_v = cand_i, cand_v

    print(ans_i)
