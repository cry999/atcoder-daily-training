N, K = map(int, input().split())
sushi = []

for _ in range(N):
    _type, deliciousness = map(int, input().split())
    sushi.append((deliciousness, _type))

sushi.sort()

selected_type = [0] * (N + 1)
selected_sushi = []

score = 0
t = 0
for _ in range(K):
    deliciousness, _type = sushi.pop()
    selected_sushi.append((deliciousness, _type))
    selected_type[_type] += 1
    score += deliciousness
    if selected_type[_type] == 1:
        score += 2 * t + 1
        t += 1

ans = score
while sushi and selected_sushi:
    new_deliciousness, new_type = sushi.pop()
    if selected_type[new_type] > 0:
        # 選択されている種類の寿司を選択してもスコアは増えない。
        continue

    while selected_sushi:
        old_deliciousness, old_type = selected_sushi.pop()
        if selected_type[old_type] == 1:
            # 選択されているのが1つのネタを新しいものと変えてもおいしさボーナス
            # は変わらないのでスコアは増えない。
            continue
        score -= old_deliciousness
        score += new_deliciousness
        score += 2 * t + 1
        t += 1
        selected_type[old_type] -= 1
        selected_type[new_type] += 1
        break
    ans = max(ans, score)
print(ans)
