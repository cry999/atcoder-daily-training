import os


N = int(input())
S, T = input(), input()


def debug(*args, **kwargs):
    if os.getenv('DEBUG', '0') == '1':
        print(*args, **kwargs)


def cyclic_perm(f: dict[str, str]) -> (list[set[int]], set[int]):
    cyclic_perms = []
    not_cyclics = set()
    for s in f.keys():
        debug('checking', s)
        if s in not_cyclics:
            # すでに巡回置換に含まれないことがわかっているため continue
            debug('  already not cyclic')
            continue
        if any(s in p for p in cyclic_perms):
            debug('  already cyclic')
            # すでに巡回置換に含まれていることがわかっているため continue
            continue

        used = set()
        cur = s
        used.add(cur)
        debug('  start traversal')
        while True:
            debug(f'    at {cur=}')
            _next = f.get(cur, '')
            if cur == 'a':
                debug(f'    at a -> {_next}: {used=}')
            if not _next or _next not in f:
                # 終端に到達
                # 利用したものは全部巡回置換に含まれない
                debug('  reached end:', used)
                not_cyclics = not_cyclics.union(used)
                break
            if _next in used:
                # 巡回置換発見
                debug('  found cyclic perm at:', _next, used)
                tail = cur
                head = _next
                cyclic_perm = set()
                # next から head までたどって巡回置換を記録する。
                while head != tail:
                    cyclic_perm.add(head)
                    head = f[head]
                cyclic_perm.add(tail)
                cyclic_perms.append(cyclic_perm)
                not_cyclics = not_cyclics.union(used.difference(cyclic_perm))
                debug('  cyclic perm:', cyclic_perm)
                debug('  not cyclics now:', not_cyclics)
                debug('  done traversal:', used)
                break

            used.add(_next)
            cur = _next

    return cyclic_perms, not_cyclics

# 1. 置換か？（全単射か？全単射に書き換えられるか？)
# 2. 最小の互換積は？


# f[s] := s -> t
# r[t] := INVERSE f
f = {}
r = {}
for s, t in zip(S, T):
    if t != f.get(s, t):
        # f は写像でないといけないので f(s) != t は矛盾
        print(-1)
        exit()
    f[s] = t
    r[t] = r.get(t, set())
    r[t].add(s)

debug(f, r)
# この時点で f は写像。
# 写像先を像とみなすので全射でもある。

# 巡回置換を見つける。


cyclic_perms, not_cyclics = cyclic_perm(f)

debug('cyclic_perms:', cyclic_perms)
debug('not_cyclics:', not_cyclics)


# 単写とするため、任意の t について len(r[s]) == 1 とする。
cnt = 0
for t, ss in r.items():
    if len(ss) <= 1:
        continue
    debug('making single mapping for', t, 'from', ss)
    debug('  not_cyclic?:', [x for x in ss if x in not_cyclics])
    if t in ss:
        # t が ss に含まれる <-> s = t なので置換から省略して良い。
        left = t
    elif any(x for x in ss if x in not_cyclics):
        # 巡回置換に含まれないものがあればそれを left にする。
        left = next(x for x in ss if x in not_cyclics)
    else:
        # それ以外はどれも同じとみなして先頭要素だけ残す。
        left = next(x for x in ss)

    r[t] = {left}
    rest = filter(lambda x: x != left, ss)

    # rest を left に変換する
    for rr in rest:
        cnt += 1
        del f[rr]

# # f[s] = s となっているものは変換不要なので消しとく。
# for s, t in f.copy().items():
#     if s == t:
#         del f[s]
#         del r[t]

# ここまでで f は全単射（置換）になっているはず。
debug(f, r, cnt)

# 再度巡回置換を見つける。
cyclic_perms, not_cyclics = cyclic_perm(f)

debug('second cyclic perm:', f, r)

# あとは、 m 次の巡回置換は m+1 回の変換で T と一致可能。ただし、m >= 2 については
# 一時置き場が必要なので、全ての文字が巡回置換で利用されている場合は達成不可能。
# あくまで、m >= 2 の巡回置換が存在する場合のみなので注意。
if any(cp for cp in cyclic_perms if len(cp) > 1) \
        and sum(len(cp) for cp in cyclic_perms) == 26:
    print(-1)
    exit()

# その他は順番に気をつければそれぞれ 1 回の変換で S -> T に変換できる。
for cyclic_perm in cyclic_perms:
    if len(cyclic_perm) == 1:
        # 1 要素の巡回置換は変換不要
        continue
    cnt += len(cyclic_perm)+1
cnt += len(not_cyclics)

print(cnt)
