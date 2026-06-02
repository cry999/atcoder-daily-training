N, W = map(int, input().split())
blocks = [tuple(map(int, input().split())) for _ in range(N)]
vanish_time = [float("inf")] * N

# lines[x] := x にあるブロックを y の降順でもつ
lines = [[] for _ in range(W)]
for i, (x, y) in enumerate(blocks):
    lines[x - 1].append((y, i))

for i in range(W):
    lines[i].sort(reverse=True)

t = 0
while True:
    for i in range(W):
        if not lines[i]:
            break
        t = max(t, lines[i][-1][0])
    else:
        for i in range(W):
            y, j = lines[i].pop()
            vanish_time[j] = t
        continue
    break

Q = int(input())
for _ in range(Q):
    t, a = map(int, input().split())
    if vanish_time[a - 1] > t:
        # 消滅時間が t よりも後なら残っている。
        # 消滅時間ちょうどは消えているので等号はいらない。
        print("Yes")
    else:
        print("No")
