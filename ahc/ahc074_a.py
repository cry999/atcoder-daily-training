# 商品ペアの共通模様＋単窓の補助紙。各ページを専用窓から取り出す。
# 詳細・比較結果・再実行方法: ahc/ahc074/README.md
import sys, random

def main():
    read = sys.stdin.readline
    line = read()
    if not line or line.strip() == '-1':
        return
    (n, k, p, r) = map(int, line.split())
    strings = [read().strip() for _ in range(p)]
    codes = [sum(((c == '1') << j for (j, c) in enumerate(s))) for s in strings]
    h = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    rng = random.Random(74)
    handles = list(range(h))
    content = list(range(h, 64))
    cm = sum((1 << j for j in content))
    flip = sum(((sum((code >> j & 1 for code in codes)) < p // 2) << j for j in content))
    codes = [code ^ flip for code in codes]
    c = k - len(content)
    # 本体部分の差が小さい商品から組にする。
    edges = []
    hm = sum((1 << j for j in handles))
    for a in range(p):
        for b in range(a):
            if ~(codes[a] ^ codes[b]) & hm:
                edges.append((((codes[a] ^ codes[b]) & cm).bit_count(), a, b))
    edges.sort()
    used = set()
    clusters = []
    for (cost, a, b) in edges:
        if a not in used and b not in used and (len(used) // 2 < p - c):
            used.add(a)
            used.add(b)
            clusters.append([a, b])
    clusters += [[a] for a in range(p) if a not in used]

    def distance(a, b):
        return ((codes[a] ^ codes[b]) & cm).bit_count() if ~(codes[a] ^ codes[b]) & hm else 999
    # 相手交換と単独商品への入れ替えで、補助紙を減らす。
    for _ in range(3):
        improved = False
        rng.shuffle(clusters)
        for i in range(c):
            if len(clusters[i]) != 2:
                continue
            (a, b) = clusters[i]
            for j in range(i + 1, c):
                other = clusters[j]
                if len(other) == 1:
                    d = other[0]
                    old = distance(a, b)
                    (da, db) = (distance(a, d), distance(b, d))
                    if min(da, db) < old:
                        if da <= db:
                            (clusters[i], clusters[j]) = ([a, d], [b])
                            b = d
                        else:
                            (clusters[i], clusters[j]) = ([b, d], [a])
                            (a, b) = (b, d)
                        improved = True
                else:
                    (x, y) = other
                    old = distance(a, b) + distance(x, y)
                    (da, db) = (distance(a, x) + distance(b, y), distance(a, y) + distance(b, x))
                    if min(da, db) < old:
                        if da <= db:
                            (clusters[i], clusters[j]) = ([a, x], [b, y])
                            b = x
                        else:
                            (clusters[i], clusters[j]) = ([a, y], [b, x])
                            b = y
                        improved = True
        if not improved:
            break
    if len(clusters) != c:
        return simple(n, k, r, strings, read)
    sizes = [c // (2 * h) * 2] * h
    for g in range((c - sum(sizes)) // 2):
        sizes[g] += 2
    assert sum(sizes) == c
    slots = [[[] for _ in range(2)] for g in range(h)]
    choices = []
    for cl in clusters:
        candidates = []
        for (g, j) in enumerate(handles):
            colors = [codes[a] >> j & 1 for a in cl]
            if min(colors) == max(colors):
                candidates.append((g, colors[0]))
        choices.append(candidates)
    # 各取っ手の白黒を交互にし、1 手で色を変えられるようにする。
    capacity = {(g, col): sizes[g] // 2 for g in range(h) for col in range(2)}
    assigned = {}

    def put(i, seen):
        for gc in sorted(choices[i], key=lambda z: len(slots[z[0]][z[1]]) / max(1, capacity[z])):
            if gc in seen:
                continue
            seen.add(gc)
            (g, col) = gc
            if len(slots[g][col]) < capacity[gc]:
                slots[g][col].append(i)
                assigned[i] = gc
                return True
            for old in slots[g][col][:]:
                if put(old, seen):
                    slots[g][col].remove(old)
                    slots[g][col].append(i)
                    assigned[i] = gc
                    return True
        return False
    for i in sorted(range(c), key=lambda i: len(choices[i])):
        if not put(i, set()):
            return simple(n, k, r, strings, read)
    pages = []
    groups = []
    member = [0] * p
    pagecolor = []
    for g in range(h):
        group = []
        for (i0, i1) in zip(slots[g][0], slots[g][1]):
            for i in (i0, i1):
                cl = clusters[i]
                base = codes[cl[0]]
                for a in cl[1:]:
                    base &= codes[a]
                j = handles[g]
                opaque = cm | 1 << j
                for a in cl:
                    member[a] = len(content) + len(pages)
                group.append(len(content) + len(pages))
                pages.append((opaque, base & opaque))
                pagecolor.append(base >> j & 1)
        groups.append(group)
    masks = [1 << j for j in content] + [x[0] for x in pages]
    blacks = [1 << j for j in content] + [x[1] for x in pages]
    order = list(range(k))
    loc = [0] * k
    for (g, group) in enumerate(groups):
        for item in group:
            loc[item] = g
    current = -1
    for (opaque, black) in zip(masks, blacks):
        print(''.join((str((black ^ flip) >> j & 1) if opaque >> j & 1 else '.' for j in range(n))))
    sys.stdout.flush()
    tops = [0] * h
    for turn in range(r):
        line = read()
        if not line or line.strip() == '-1':
            return
        a = int(line)
        target = codes[a]
        page = member[a]
        g = loc[page]
        moves = []

        def move(item, d):
            ix = order.index(item)
            order.pop(ix)
            order.insert(d, item)
            moves.append((item, d))

        def retire(group):
            item = groups[group][tops[group]]
            move(item, k - 1)
            tops[group] = (tops[group] + 1) % len(groups[group])
        # 同じ色を保ちたい場合、前のページを補助紙の直下へ戻す。
        if current >= 0:
            oldg = loc[current]
            if oldg != g and blacks[current] >> handles[oldg] & 1 == target >> handles[oldg] & 1 or current == page:
                move(current, len(content))
            else:
                retire(oldg)
        while groups[g][tops[g]] != page:
            retire(g)
        patches = target & cm & ~blacks[page]
        # 差し込み位置を全探索。前方の不要紙を下げるか、後方の必要紙を上げる。
        bank = order[:len(content)]
        score = best = patches.bit_count()
        cut = 0
        for (t, item) in enumerate(bank):
            bit = 1 << content[item]
            if patches & bit:
                score -= 1
            elif not target & bit:
                score += 1
            if score < best:
                best = score
                cut = t + 1
        count = cut
        for item in bank[cut:]:
            if patches >> content[item] & 1:
                move(item, 0)
                count += 1
        for item in bank[:cut]:
            if not target >> content[item] & 1:
                move(item, len(content) - 1)
                count -= 1
        move(page, count)
        current = page
        for (group, j) in enumerate(handles):
            if group != g and blacks[groups[group][tops[group]]] >> j & 1 != target >> j & 1:
                retire(group)
        print(str(len(moves)) + ''.join((f'\n{x} {d}' for (x, d) in moves)), flush=True)

def simple(n, k, r, products, read):
    if k < 2 * n:
        return
    sheets = []
    for j in range(n):
        for color in '01':
            sheets.append('.' * j + color + '.' * (n - j - 1))
    print('\n'.join(sheets + ['.' * n] * (k - 2 * n)), flush=True)
    current = [0] * n
    for _ in range(r):
        line = read()
        if not line or line.strip() == '-1':
            return
        target = products[int(line)]
        moves = []
        for (j, c) in enumerate(target):
            color = int(c)
            if current[j] != color:
                moves.append((2 * j + current[j], 2 * j + 1))
                current[j] = color
        print(str(len(moves)) + ''.join((f'\n{a} {d}' for (a, d) in moves)), flush=True)
if __name__ == '__main__':
    main()
