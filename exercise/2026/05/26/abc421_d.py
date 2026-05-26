rt, ct, ra, ca = map(int, input().split())
N, M, L = map(int, input().split())

DIRS = [
    (0, 1),  # R
    (1, 0),  # D
    (0, -1),  # L
    (-1, 0),  # U
]
DIRS_MAP = {
    "R": 0,
    "D": 1,
    "L": 2,
    "U": 3,
}

takahashi_traces = []
for _ in range(M):
    dir, num = input().split()
    takahashi_traces.append([DIRS_MAP[dir], int(num)])
takahashi_traces.reverse()

aoki_traces = []
for _ in range(L):
    dir, num = input().split()
    aoki_traces.append([DIRS_MAP[dir], int(num)])
aoki_traces.reverse()


ans = 0
rot = 0
while takahashi_traces and aoki_traces:
    # print("---")
    takahashi_dir, takahashi_num = takahashi_traces[-1]
    aoki_dir, aoki_num = aoki_traces[-1]

    move_num = min(takahashi_num, aoki_num)
    takahashi_dir = (takahashi_dir - rot) % 4
    aoki_dir = (aoki_dir - rot) % 4

    # print(f"takahashi: {takahashi_dir}@{move_num}")
    # print(f"aoki: {aoki_dir}@{move_num}")

    # 簡単のため、高橋が右に動くように座標を回転する。
    for _ in range(takahashi_dir):
        rt, ct = -ct, rt
        ra, ca = -ca, ra
    # print(f"takahashi: ({rt}, {ct})")
    # print(f"aoki: ({ra}, {ca})")
    aoki_dir = (aoki_dir - takahashi_dir) % 4
    rot = (rot + takahashi_dir) % 4
    takahashi_dir = 0

    # 交わるのは 4 パターン
    # 1. 青木が下から上に動くパターン
    if aoki_dir == 3 and rt < ra <= rt + move_num and ra - rt == ca - ct:
        ans += 1
    # 2. 青木が上から下に動くパターン
    if aoki_dir == 1 and ra < rt <= ra + move_num and rt - ra == ca - ct:
        ans += 1
    # 3. 青木が右から左に動くパターン
    if (
        aoki_dir == 2
        and rt == ra
        and 0 < ca - ct <= 2 * move_num
        and (ca - ct) % 2 == 0
    ):
        ans += 1
    # 4. 同じ位置からスタートして、同じ方向に動くパターン
    if aoki_dir == 0 and rt == ra and ct == ca:
        ans += move_num

    rt += 0
    ct += move_num

    ra += DIRS[aoki_dir][0] * move_num
    ca += DIRS[aoki_dir][1] * move_num
    # print(f"  -> takahashi: ({rt}, {ct})")
    # print(f"  -> aoki: ({ra}, {ca})")

    takahashi_traces[-1][1] -= move_num
    if takahashi_traces[-1][1] == 0:
        takahashi_traces.pop()

    aoki_traces[-1][1] -= move_num
    if aoki_traces[-1][1] == 0:
        aoki_traces.pop()

print(ans)
