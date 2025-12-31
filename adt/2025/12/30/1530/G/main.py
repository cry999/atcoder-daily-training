from sortedcontainers import SortedList
import sys, os


DEBUG = os.environ.get("DEBUG", "0") == "1"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N, K = map(int, input().split())
(*P,) = map(int, input().split())

field = SortedList()
eat_timing = [-1] * N
decks = []

for j, x in enumerate(P):
    debug(f"turn={j}, {x=}")
    # debug(f"  {field=}")
    # debug(f"  {eat_timing=}")
    # debug(f"  {decks=}")
    i = field.bisect_left((x, 0, 0))
    if i == len(field):
        if K != 1:
            debug(f"  append new: {(x, 1, len(decks))=}")
            field.add((x, 1, len(decks)))
            decks.append([x])
        else:  # K == 1 の場合は即座に食べる
            eat_timing[x - 1] = j + 1
    else:
        debug(f"  update existing: {field[i]=}")
        if field[i][1] + 1 == K:
            debug(f"  eat: {field[i]=}")
            # 食べる
            for k in decks[field[i][2]]:
                eat_timing[k - 1] = j + 1  # すでに山札に積んであるもの
            eat_timing[x - 1] = j + 1  # 今回積む予定だったもの
            field.remove(field[i])
        else:
            debug(f"  grow: {field[i]=}")
            append = (x, field[i][1] + 1, field[i][2])
            field.remove(field[i])
            field.add(append)
            decks[field[i][2]].append(x)

for t in eat_timing:
    print(t)
