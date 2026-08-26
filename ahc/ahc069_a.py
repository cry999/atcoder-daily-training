import math
import sys
from collections import deque

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class GroupInfo:
    def __init__(self, s: int, t: int, p: int, v: int):
        self.s = s  # 到着時刻
        self.t = t  # 退去時刻
        self.p = p  # 人数
        self.v = v  # 基本支払額
        self.c = None  # コンパクト度（配置後に設定）
        self.pos = None  # 占有マスの座標 [(行, 列), ...]（配置後に設定）


def find_region(grid: list[list[int]], owner: list[list[int]], n: int, p: int):
    """
    上の行から順に最初の空き芝生マスを探し、そこから BFS で p マス集める。
    p マス集められれば座標リストを、集められなければ None を返す。
    """

    # 最初の空き芝生マスを探す
    start = None
    for x in range(n):
        for y in range(n):
            if grid[x][y] == "." and owner[x][y] == -1:
                start = (x, y)
                break
        if start is not None:
            break
    if start is None:
        return None

    # start から BFS。取り出したマスを順に領域へ加え、p 個に達したら止める。
    visited = [[False] * n for _ in range(n)]
    visited[start[0]][start[1]] = True
    queue = deque([start])
    region = []
    while queue and len(region) < p:
        x, y = queue.popleft()
        region.append((x, y))
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < n
                and 0 <= ny < n
                and not visited[nx][ny]
                and grid[nx][ny] == "."
                and owner[nx][ny] == -1
            ):
                visited[nx][ny] = True
                queue.append((nx, ny))

    return region if len(region) == p else None


def compactness(region: list[tuple[int, int]], p: int) -> float:
    """コンパクト度を返す。"""
    cells = set(region)
    perimeter = 0
    for x, y in region:
        for dx, dy in DIRS:
            if (x + dx, y + dy) not in cells:
                perimeter += 1
    return 4 * math.sqrt(p) / perimeter


def main():
    n, m, r = input().split()
    n, m = int(n), int(m)
    grid = [input() for _ in range(n)]

    # owner[x][y]: そのマスを占有しているグループ番号。空きは -1。
    owner = [[-1] * n for _ in range(n)]
    # これまで到着した全グループ
    groups = []

    for i in range(m):
        _gi, s, t, p, v = map(int, input().split())
        group = GroupInfo(s, t, p, v)
        groups.append(group)

        # 退去時刻が現在時刻 s より前のグループを解放する
        for g in groups:
            if g.pos is not None and g.t < s:
                for x, y in g.pos:
                    owner[x][y] = -1
                g.pos = None

        # 移動は行わない
        print(0)

        region = find_region(grid, owner, n, p)
        if region is not None:
            # 割り当てる: owner を更新し、コンパクト度と占有マスを記録する
            for x, y in region:
                owner[x][y] = i
            group.pos = region
            group.c = compactness(region, p)
            print("Yes")
            for x, y in region:
                print(x, y)
        else:
            # 拒否
            print("No")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
