"""Independent abstract test of same-cost group-prefix rebuilding."""
import itertools
import random

rng = random.Random(74)
checks = 0
for size in [2, 4, 6, 8, 10, 12]:
    for bits in itertools.product([0, 1], repeat=size // 2):
        color = [c for b in bits for c in [b, 1 - b]]
        for rank in range(size):
            for rep in range(10):
                weight = [rng.randint(1, 4) for _ in range(size)]
                order = list(range(size))
                page = order[rank]
                end = (rank // 2 + 1) * 2
                colors = [[], []]
                for item in order[:end]:
                    if item != page:
                        colors[color[item]].append(item)
                for row in colors:
                    row.sort(key=lambda i: -weight[i])
                desired = [page, colors[1 - color[page]].pop(0)]
                pairs = []
                for x, y in zip(colors[0], colors[1]):
                    if weight[x] < weight[y]:
                        x, y = y, x
                    pairs.append((x, y))
                pairs.sort(key=lambda ab: -weight[ab[0]] - weight[ab[1]])
                desired.extend(i for pair in pairs for i in pair)
                placed = {page}
                if rank % 2 == 0:
                    placed.add(order[rank + 1])
                original = order[:]
                for item in original[:rank]:
                    assert order[0] == item
                    ix = desired.index(item)
                    anchor = next(z for z in reversed(desired[:ix]) if z in placed)
                    dest = order.index(anchor)
                    order.remove(item)
                    order.insert(dest, item)
                    placed.add(item)
                assert order == desired + original[end:]
                assert all(color[order[i]] != color[order[i + 1]]
                           for i in range(0, size, 2))
                checks += 1
print('abstract rebuild checks:', checks)
