N, M = map(int, input().split())

blocks = set()
num_blocks = 0

drcs = [(0, 0), (0, 1), (1, 0), (1, 1)]

for _ in range(M):
    R, C = map(int, input().split())

    if any((R+dr, C+dc) in blocks for dr, dc in drcs):
        continue

    num_blocks += 1
    for dr, dc in drcs:
        blocks.add((R+dr, C+dc))

print(num_blocks)
