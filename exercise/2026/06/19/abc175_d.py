N, K = map(int, input().split())
(*P,) = map(lambda x: int(x) - 1, input().split())
(*C,) = map(int, input().split())


def score_generator(scores: list[int]):
    cycle_score = sum(scores)
    length = len(scores)

    # 各頂点から始めて、1周未満だけ実際に試す。
    limit = min(K, length)
    for start in range(length):
        # 1周未満のスコアを計算する。
        path_score = 0
        for steps in range(1, limit + 1):
            path_score += scores[(start + steps) % length]

            # cycle_score が正の時は、回れるだけ回ってみる。
            yield path_score + max(0, (K - steps) // length * cycle_score)

    return


visited = [False] * N

ans = max(C)
for i in range(N):
    if visited[i]:
        continue

    cycle = []

    cur = i
    while not visited[cur]:
        visited[cur] = True
        cycle.append(cur)
        cur = P[cur]

    # この閉路を回る時のベストスコアを考える
    ans = max(ans, max(score_generator([C[v] for v in cycle])))

print(ans)
