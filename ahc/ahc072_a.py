import heapq
import math
import random
import sys
import time
from collections.abc import Callable

# ============================================================
# 基本処理: 問題のルールと汎用処理。戦略の改善では触らない。
# - 盤面を変えるのは Board.jump だけ。jump の assert で操作の合法性を
#   確かめるので、ロジックをどう変えても不正な出力に気づける。
# - 基本処理からロジックは呼ばない。
# ============================================================

# ---- 型 ----
Pos = tuple[int, int]
Grid = list[list[int]]  # マスごとの値 (距離や色)
Towers = list[list[list[int]]]  # マスごとの塔

# ---- 問題の定数 ----
INF = 10**18
MAX_H = 8  # 問題で決まっている塔の高さの上限
DIRS: dict[str, Pos] = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
DIR_OF = {v: d for d, v in DIRS.items()}  # 変化量 → 方向
COLORS = "abcdefghijkl"


class Board:
    """盤面の状態と、問題のルールに沿った操作をまとめたもの。

    塔の中身は height / top で読み、盤面を変えるのは jump だけにする。

    Attributes:
        N: 盤面の一辺。
        K: 色の数。
        C: 入力の盤面。
        nest: nest[i][j] はマス (i,j) にある巣の色 (なければ -1)。
        nests: nests[c] は色 c の巣の位置。
        dist: dist[c][i][j] はマス (i,j) から色 c の巣までの距離。
        ops: 出力する操作列。
    """

    def __init__(self, N: int, K: int, C: list[str]) -> None:
        self.N = N
        self.K = K
        self.C = C
        # _tower[i][j]: マス (i,j) の塔。下から順に色を並べたリスト
        self._tower = self._init_towers()
        self.nest, self.nests = self._init_nests()
        self.dist = [self.bfs(*self.nests[c]) for c in range(K)]
        self.ops: list[str] = []

    def _init_towers(self) -> Towers:
        """初期状態の塔を作る。

        Returns:
            tower[i][j]: 小文字のマスには、その色のスライム 1 匹だけの塔。
        """
        tw: Towers = [[[] for _ in range(self.N)] for _ in range(self.N)]
        for i in range(self.N):
            for j in range(self.N):
                if self.C[i][j].islower():
                    tw[i][j].append(COLORS.index(self.C[i][j]))
        return tw

    def _init_nests(self) -> tuple[Grid, list[Pos]]:
        """巣の位置を調べる。

        Returns:
            (nest, nests): nest[i][j] はマス (i,j) の巣の色 (なければ -1)、
            nests[c] は色 c の巣の位置 (i, j)。
        """
        nest = [[-1] * self.N for _ in range(self.N)]
        nests = [(-1, -1)] * self.K
        for i in range(self.N):
            for j in range(self.N):
                if self.C[i][j].isupper():
                    c = COLORS.index(self.C[i][j].lower())
                    nest[i][j] = c
                    nests[c] = (i, j)
        return nest, nests

    def height(self, i: int, j: int) -> int:
        """マス (i,j) の塔の高さ。"""
        return len(self._tower[i][j])

    def top_color(self, i: int, j: int) -> int:
        """マス (i,j) の塔の一番上の色 (塔がなければ -1)。"""
        t = self._tower[i][j]
        return t[-1] if t else -1

    def remaining(self) -> int:
        """盤面に残っているスライムの数 (スコアの E)。"""
        return sum(len(t) for row in self._tower for t in row)

    def score(self) -> int:
        """今の操作列の絶対スコア T + 100000 E (小さいほど良い)。"""
        return len(self.ops) + 100000 * self.remaining()

    def copy(self) -> "Board":
        """盤面を複製する (入力と巣の情報は共有し、塔と操作列を複製する)。"""
        b = Board.__new__(Board)
        b.N, b.K, b.C = self.N, self.K, self.C
        b._tower = [[t[:] for t in row] for row in self._tower]
        b.nest, b.nests, b.dist = self.nest, self.nests, self.dist
        b.ops = self.ops[:]
        return b

    def is_floor(self, i: int, j: int) -> bool:
        """(i,j) が盤面内の床かどうか。"""
        return 0 <= i < self.N and 0 <= j < self.N and self.C[i][j] != "#"

    def bfs(self, si: int, sj: int) -> Grid:
        """(si,sj) から壁を避けて 1 マスずつ歩いたときの距離を求める。

        Args:
            si, sj: 始点。

        Returns:
            ds[i][j]: 始点から (i,j) までの距離 (届かなければ INF)。
        """
        ds = [[INF] * self.N for _ in range(self.N)]
        ds[si][sj] = 0
        q = [(si, sj)]
        for i, j in q:
            for di, dj in DIRS.values():
                ni, nj = i + di, j + dj
                if not self.is_floor(ni, nj) or ds[ni][nj] != INF:
                    continue
                ds[ni][nj] = ds[i][j] + 1
                q.append((ni, nj))
        return ds

    def path_to(self, ds: Grid, ti: int, tj: int) -> list[str]:
        """bfs の結果から、始点から (ti,tj) までの最短経路を求める。

        (ti,tj) から距離が 1 ずつ減るマスを逆にたどって復元する。

        Args:
            ds: bfs(始点) の結果。
            ti, tj: 終点。

        Returns:
            始点から順に並べた方向 ("U"/"D"/"L"/"R") のリスト。
        """
        res: list[str] = []
        i, j = ti, tj
        while ds[i][j] > 0:
            for d, (di, dj) in DIRS.items():
                pi, pj = i - di, j - dj
                if not self.is_floor(pi, pj) or ds[pi][pj] != ds[i][j] - 1:
                    continue
                res.append(d)
                i, j = pi, pj
                break
        return res[::-1]

    def _go_home(self, i: int, j: int) -> None:
        """マス (i,j) で帰巣を行う。

        巣のマスなら、塔の一番上が巣の色である限り取り除く。
        """
        c = self.nest[i][j]
        if c == -1:
            return
        t = self._tower[i][j]
        while t and t[-1] == c:
            t.pop()

    def jump(self, i: int, j: int, k: int, d: str, ln: int) -> Pos:
        """宙返りジャンプを 1 回行い、ops に記録する。

        (i,j) の塔の下 k 匹を残し、上の一団を上下反転して d 方向へ ln マス先の
        塔に積む。その後、出発点と着地点で帰巣を行う。
        不正な操作なら assert で止める。

        Args:
            i, j: 出発点。
            k: 下に残す匹数。
            d: 方向 ("U"/"D"/"L"/"R")。
            ln: 飛距離 (1 <= ln <= k+1)。

        Returns:
            着地点 (ni, nj)。
        """
        t = self._tower[i][j]
        h = len(t)
        assert 0 <= k < h and 1 <= ln <= k + 1

        di, dj = DIRS[d]
        for s in range(1, ln + 1):
            assert self.is_floor(i + di * s, j + dj * s)

        ni, nj = i + di * ln, j + dj * ln
        assert self.height(ni, nj) + (h - k) <= MAX_H

        grp = t[k:]
        del t[k:]

        self._tower[ni][nj].extend(reversed(grp))
        self._go_home(i, j)
        self._go_home(ni, nj)
        self.ops.append(f"{i} {j} {k} {d} {ln}")
        return ni, nj


# ============================================================
# ロジック: 戦略。スコア改善はここを触る。
# - 盤面は height / top などで読むだけにして、動かすときは必ず jump を通す。
# ============================================================

# ---- 戦略のパラメータ ----
# 試す案の候補 (時間の許す限り、この順に全部解いて一番良いものを選ぶ)。
# - ("tree", BUILD_H): 色ごとに木を作ってペアで合流させる方式 (Solver)。
#   BUILD_H は自分で組み上げる塔の最終的な高さの上限。7 にしておけば、
#   運ぶ途中で高さ 1 のマスに着地しても MAX_H に収まる。低くすると、ペアの
#   合流 (合計の高さ MAX_H 以下) がしやすくなる。
# - ("bus", RADIUS): 1 つの塔が巡回しながら拾い、巣を回る方式 (BusSolver)。
#   RADIUS は次に運ぶ色をついでに拾う距離 (手数) の上限。0 なら 1 色ずつ。
# - ("plan", 0): ケース全体を、ルートを計画したバスで運ぶ
#   (BusSolver._planned_sa、焼きなまし法)。
# よく最良になる順に並べる (100 ケースで最良になった件数: tree=7 が最多、
# 次いで plan, 6, 5。ケース全体を 2 色の連鎖バスで解く RADIUS=1, 3 と、
# 最良になることがほとんどない bus=0, tree=4 は外した)。
CANDIDATES = (
    ("tree", 7),
    ("plan", 0),
    ("tree", 6),
    ("tree", 5),
)
# バスに乗せる匹数の上限。拾うときは着地先 (1 匹) と合わせて MAX_H 以下。
BUS_CAP = MAX_H - 1
# 色ごと (1 色・ペア) のバスのルートを局所探索で改善する回数。
PLAN_ITERS = 2000
# ケース全体を運ぶ計画型バス ("plan" の案) の焼きなまし法に使う時間 (秒)。
PLAN_TIME_ALL = 0.5
# 計画の見積もりで、並びの決まりを満たす偶奇で着けない区間に足す罰の手数。
PARITY_PENALTY = 30
# プログラム全体で使ってよい時間 (秒)。制限は 2 秒。
TIME_LIMIT = 1.5

# ---- 型 ----
Slime = tuple[int, int, int]  # (巣までの距離, i, j)
Walk = tuple[int, int, list[tuple[str, int]]]  # 一団のいるマス と 手順
# 合流の見積もりで使い回す (盤面の高さ, 根の塔の元のマスを空にした高さ, メモ)
MergeCache = tuple[list[int], list[int], dict]
# 色の順番と見積もりの手数 (木の案の間で使い回す)
Plan = tuple[list[int], int]


class Solver:
    """戦略に沿って、全スライムを巣へ返す操作を board に積む。

    公開するのは solve だけ。盤面は board の height / top_color などで読み、
    動かすときは必ず board.jump を通す。
    マスは内部では 1 次元の番号 c = i*N+j で扱う。
    """

    def __init__(
        self,
        board: Board,
        build_h: int = 7,
        plan: Plan | None = None,
    ) -> None:
        self.board = board
        self.build_h = build_h  # 自分で組み上げる塔の最終的な高さの上限
        # 色の順番。None なら solve で求める (求めた結果は他の案で
        # 使い回せるように self.plan に残す)
        self.plan = plan
        N = board.N
        # rays[c]: マス c から各方向へ、床が続く限り (最大 MAX_H マス) 並べたマス。
        # 1 回のジャンプで着地できるのは、この先頭 (下の匹数+1) マスのどれか。
        self.rays: list[list[list[int]]] = []
        for i in range(N):
            for j in range(N):
                rs = []
                for di, dj in DIRS.values():
                    r = []
                    for s in range(1, MAX_H + 1):
                        if not board.is_floor(i + di * s, j + dj * s):
                            break
                        r.append((i + di * s) * N + j + dj * s)
                    rs.append(r)
                self.rays.append(rs)

    def solve(self) -> None:
        """全スライムを巣へ返す操作を board.ops に積む。

        1. 色の順番を決める (_decide_order)。このときの運び方は、他の色が
           全員残っている盤面で決めた経路に固定して見積もる (_plan_walks)。
        2. 合流で得をする見積もりが最大になるように、2 色ずつペアにする
           (_make_pairs)。得をしない色はペアにしない。
           1 の色順 DP は、self.plan が与えられていれば省く (他の案の結果を
           使い回す)。ペアは根の塔の大きさ (BUILD_H) で変わるので毎回決める。
        3. その順番で、ペアの 2 色は同時に処理する (_carry_pair)。
           ペアの相手がいない色は、1 色だけで処理する (_carry)。
           ただし色 (ペアなら 2 色) ごとに、盤面を複製してバス方式でも
           運んでみて、手数が少ないほうを採用する (_carry_best)。
        """
        board = self.board
        walks = [self._plan_walks(k) for k in range(board.K)]
        if self.plan is None:
            self.plan = self._decide_order(walks)
        order, expected = self.plan
        partner = self._make_pairs(walks)
        self.n_merge = 0  # 合流させた根の塔の組の数 (確認用)
        self.postponed = 0  # 後回しにした回数 (確認用)
        self.n_unride = 0  # 乗り先へ届かず根にした乗る組の数 (確認用)
        self.crossings = 0  # 分けて越えた回数 (確認用)
        self.chosen: dict[str, int] = {}  # 採用した運び方の回数 (確認用)
        done: set[int] = set()
        for k in order:
            if k in done:
                continue
            p = partner[k]
            self._carry_best(k, p)
            done |= {k, p} - {-1}
        print(
            f"order={order} expected={expected} actual={len(self.board.ops)} "
            f"merge={self.n_merge} postponed={self.postponed} "
            f"unride={self.n_unride} crossings={self.crossings} "
            f"chosen={self.chosen} "
            f"pairs={sum(p != -1 for p in partner) // 2}",
            file=sys.stderr,
        )

    def _carry_best(self, k: int, p: int) -> None:
        """色 k (ペアなら k と p) を、いくつかの運び方のうち最も良いもので運ぶ。

        今の盤面を複製して各運び方を最後まで試し、手数が最も少ない盤面を
        self.board として採用する。失敗した運び方は候補から外す。
        1 色のとき:
        - 木の方式 (_carry)
        - その色を集めるバス (ルートを計画してから走る。_planned)
        ペアのとき:
        - 木の方式でペアの根の塔を合流させる (_carry_pair)
        - 1 色ずつのバスを k, p の順に出す
        - ペアの 2 色をまとめて運ぶバス (ルートを計画してから走る。_planned_pair)
        - ペアを組まずに、k, p の順に 1 色ずつ上の 1 色のときの良いほうで運ぶ
        """
        base = self.board

        def tree(b: Board) -> Board:
            self.board = b
            if p == -1:
                self._carry(k)
            else:
                self._carry_pair(k, p)
            return self.board

        def bus_each(b: Board) -> Board:
            bus = BusSolver(b, 0)
            for c in (k, p):
                if c != -1:
                    bus._planned([c], PLAN_ITERS)
            return bus.board

        def bus_pair(b: Board) -> Board:
            bus = BusSolver(b, INF)
            bus._planned_pair(k, p)
            return bus.board

        def separate(b: Board) -> Board:
            self.board = b
            self._carry_best(k, -1)
            self._carry_best(p, -1)
            return self.board

        options = [("tree", tree), ("bus", bus_each)]
        if p != -1:
            options += [("bus_pair", bus_pair), ("separate", separate)]
        results: list[tuple[int, str, Board]] = []
        for name, run in options:
            try:
                b = run(base.copy())
                results.append((b.score(), name, b))
            except Exception as e:
                print(f"{name} for {k},{p} failed: {e!r}", file=sys.stderr)
        assert results, "どの運び方も失敗した"
        _, name, best = min(results, key=lambda r: r[0])
        self.chosen[name] = self.chosen.get(name, 0) + 1
        self.board = best

    def _make_pairs(self, walks: list[list[Walk]]) -> list[int]:
        """合流で得をする見積もりの合計が最大になるように、2 色ずつペアにする。

        色 a と b の得 (_pair_gain) を全組について見積もり、得の合計が最大の
        組み方 (最大重みマッチング) を bit DP で求める。得をしない色は
        ペアにしない。

        Args:
            walks: walks[k] は色 k の _plan_walks の結果。

        Returns:
            partner[k]: 色 k のペアの相手 (いなければ -1)。
        """
        K = self.board.K
        roots = [self._roots_of(k, walks[k]) for k in range(K)]
        gain = [[0] * K for _ in range(K)]
        for a in range(K):
            for b in range(a + 1, K):
                gain[a][b] = gain[b][a] = self._pair_gain(
                    a, b, roots[a], roots[b]
                )

        # f[mask]: mask の色の組み方を決め終えたあとに得られる最大の得
        full = (1 << K) - 1
        f = [0] * (1 << K)
        choice = [-1] * (1 << K)  # 一番小さい未決定の色の相手 (-1 なら単独)
        for mask in range(full - 1, -1, -1):
            i = 0
            while mask >> i & 1:
                i += 1
            f[mask] = f[mask | 1 << i]
            for j in range(i + 1, K):
                if mask >> j & 1 or gain[i][j] <= 0:
                    continue
                v = gain[i][j] + f[mask | 1 << i | 1 << j]
                if v > f[mask]:
                    f[mask], choice[mask] = v, j

        partner = [-1] * K
        mask = 0
        while mask != full:
            i = 0
            while mask >> i & 1:
                i += 1
            j = choice[mask]
            if j == -1:
                mask |= 1 << i
            else:
                partner[i], partner[j] = j, i
                mask |= 1 << i | 1 << j
        return partner

    def _roots_of(self, k: int, walks: list[Walk]) -> list[tuple[int, int]]:
        """_plan_walks の結果から、色 k の根の塔の (マス, 匹数) を取り出す。

        walks は動かす順 (乗る組は遠い順、そのあと根) に並んでいるので、
        乗り先の匹数に乗る組の匹数を足していけば、根の塔の匹数がわかる。
        """
        board = self.board
        N = board.N
        home = board.nests[k][0] * N + board.nests[k][1]
        size: dict[int, int] = {}
        roots: list[tuple[int, int]] = []
        for i, j, moves in walks:
            s = i * N + j
            for d, ln in moves:
                di, dj = DIRS[d]
                i, j = i + di * ln, j + dj * ln
            t = i * N + j
            size[s] = size.get(s, 0) + 1
            if t == home:
                roots.append((s, size[s]))
            else:
                size[t] = size.get(t, 0) + size[s]
        return roots

    def _pair_gain(
        self,
        a: int,
        b: int,
        ra: list[tuple[int, int]],
        rb: list[tuple[int, int]],
    ) -> int:
        """色 a と b をペアにしたとき、根の塔の合流で得をする手数の見積もり。

        計算を軽くするため、踏み台を考えない歩数で数え、合流地点は根の塔の
        マスに限り、偶奇合わせも無視する。根の塔の組ごとに
            別々に帰る歩数 - min(相手の根へ行く + そこから先の巣 + 先の巣から後の巣)
        を求め、得の大きい組から 1 対 1 に貪欲に選んで合計する。
        """
        board = self.board
        N = board.N
        dist = board.dist
        na = board.nests[a]
        ab = dist[b][na[0]][na[1]]  # 巣 a と巣 b の間の歩数
        cand = []
        for ca, ma in ra:
            ds = board.bfs(ca // N, ca % N)
            for cb, mb in rb:
                if ma + mb > MAX_H:
                    continue
                ai, aj = divmod(ca, N)
                bi, bj = divmod(cb, N)
                alone = dist[a][ai][aj] + dist[b][bi][bj]
                meet = ds[bi][bj]
                merged = meet + ab + min(
                    dist[a][ai][aj], dist[b][ai][aj],
                    dist[a][bi][bj], dist[b][bi][bj],
                )
                if alone - merged > 0:
                    cand.append((alone - merged, ca, cb))
        cand.sort(reverse=True)
        used: set[int] = set()
        gain = 0
        for g, ca, cb in cand:
            if ca in used or cb in used:
                continue
            used |= {ca, cb}
            gain += g
        return gain

    # ---- 踏み台を考慮した運び方 (実際に動かすときに使う) ----

    def _carry(self, k: int) -> None:
        """色 k の塔を、踏み台を考慮した経路で組み上げて巣へ運ぶ。"""
        roots = self._build(k)
        self._send_home(roots)

    def _build(self, k: int) -> list[tuple[int, int]]:
        """色 k の乗る組を乗り先へ動かし、根の上に塔を組み上げる。

        乗り先は _plan_rides で、この時点の盤面での手数をもとに決める。
        経路は一団を動かす直前に、その時点の盤面で求める。動かす直前に
        求めるのは、踏み台にするスライム (同じ色で先に動いたものなど) が
        いなくなっていることがあるため。

        Returns:
            根の塔の (色, マス) のリスト。乗り先へ届かなかった乗る組も含む。
        """
        board = self.board
        N = board.N
        home = board.nests[k][0] * N + board.nests[k][1]
        h = self._heights()
        q, par = self._plan_rides(
            k, lambda i, j: self._jump_bfs(i * N + j, 1, home, h)[0]
        )
        roots: list[tuple[int, int]] = []
        for x, y in self._move_order(par):
            _, i, j = q[x]
            if y == -1:
                roots.append((k, i * N + j))
                continue
            if not self._walk_to(i, j, q[y][1] * N + q[y][2], home):
                # 他の色の高い塔に阻まれて乗り先へ届かないときは、乗るのを
                # やめて自分の塔を根として巣へ運ぶ。自分に乗ってくる仲間は
                # 遠い順に動かしているので、この時点で到着済み。
                roots.append((k, i * N + j))
                self.n_unride += 1
        return roots

    def _send_home(self, roots: list[tuple[int, int]]) -> None:
        """根の塔をそれぞれ巣へ運ぶ。

        ペアで処理しているときは他の色の高い塔が残っていて、通れないことが
        ある。届かない塔は後回しにして、他の塔が帰巣したあとに再挑戦する。
        """
        board = self.board
        N = board.N
        while roots:
            rest = []
            for k, c in roots:
                home = board.nests[k][0] * N + board.nests[k][1]
                if not self._walk_to(c // N, c % N, home, home):
                    rest.append((k, c))
            assert len(rest) < len(roots), "どの塔も巣へ運べない"
            self.postponed += len(rest)
            roots = rest

    # ---- ペアの 2 色の根の塔の合流 ----

    def _carry_pair(self, ka: int, kx: int) -> None:
        """色 ka と色 kx をペアで処理する。

        両方の色の塔を組み上げてから、帰り道が重なる根の塔どうしを
        1 対 1 で合流させる (_merge_plan)。合流した塔は先の巣でその色の
        塊が帰巣し、残りの塊が後の巣へ向かう。合流しない塔はそれぞれ巣へ運ぶ。
        得をする組から順に貪欲に決め、合流を実行する直前に今の盤面で
        見積もり直して、得をしなくなっていたら合流をやめる。
        """
        roots = self._build(ka) + self._build(kx)
        # 候補を順位付けするときは、組が違っても同じになる計算 (根の塔ごとの
        # BFS、巣からの BFS、偶奇つき BFS の表) を使い回す。偶奇つき BFS の
        # 表は、全部の根の塔の元のマスを空にした盤面で作る近似にする。
        # 実際に合流させる直前には、正確に見積もり直す。
        h = self._heights()
        h2 = h[:]
        for _, c in roots:
            h2[c] = 0
        shared: MergeCache = (h, h2, {})
        cand = []
        for ra in roots:
            for rx in roots:
                if ra[0] == ka and rx[0] == kx:
                    plan = self._merge_plan(ra, rx, shared)
                    if plan is not None:
                        cand.append((plan[0], ra, rx))
        cand.sort(reverse=True)

        used: set[tuple[int, int]] = set()
        for _, ra, rx in cand:
            if ra in used or rx in used:
                continue
            plan = self._merge_plan(ra, rx)
            if plan is None:
                continue
            used |= {ra, rx}
            self._merge(*plan[1:])
            self.n_merge += 1
        self._send_home([r for r in roots if r not in used])

    def _merge_plan(
        self,
        ra: tuple[int, int],
        rx: tuple[int, int],
        shared: "MergeCache | None" = None,
    ) -> tuple[int, int, int, int, int, int] | None:
        """根の塔 ra と rx を合流させたときに得をする手数と、そのやり方。

        合流地点 m を全マスから選ぶ。下になる塔 (bottom) が先に m へ行き、
        上になる塔 (top) が後から m に着地して乗る。bottom の元のマスを m に
        すれば、bottom は動かずに top が乗りに来る形になる。
        合流する場合の手数は
            D(bottom → m) + D(top → m) + G(m → 先の巣、偶奇指定) + D(先の巣 → 後の巣)
        で、(先の巣, bottom と top の役割) の 4 通り × 全マス m から最小を選ぶ。
        合流した直後は top の色が上にある。塔全体は 1 手ごとに反転するので、
        先の巣の色が top の色なら偶数手、そうでなければ奇数手で着く必要がある。

        Args:
            ra, rx: 根の塔の (色, マス)。
            shared: 候補の順位付け用の (盤面の高さ, 根の塔の元のマスを空にした
                高さ, 計算結果のメモ)。指定すると、BFS の結果を組の間で
                使い回す (近似)。None なら今の盤面で正確に求める。

        Returns:
            (得をする手数, bottom のマス, top のマス, 合流地点, 先の巣の色,
            後の巣の色)。得をしなければ None。
        """
        board = self.board
        N = board.N
        if shared is None:
            h = self._heights()
            h2 = h[:]
            h2[ra[1]] = h2[rx[1]] = 0  # 合流したあとは元のマスは空
            memo: dict[tuple[int, int, int, int], list] = {}
        else:
            h, h2, memo = shared
        nests = {i * N + j for i, j in board.nests}

        def jbfs(s: int, mm: int, home: int) -> list[int]:
            key = (0, s, mm, home)
            if key not in memo:
                memo[key] = self._jump_bfs(s, mm, home, h)[0]
            return memo[key]

        def parity(MM: int, home: int) -> list[list[int]]:
            key = (1, MM, home, 0)
            if key not in memo:
                memo[key] = self._parity_dist(MM, home, h2, nests - {home})
            return memo[key]

        m = {ra: h[ra[1]], rx: h[rx[1]]}
        M = m[ra] + m[rx]
        if M > MAX_H:
            return None
        home = {
            r: board.nests[r[0]][0] * N + board.nests[r[0]][1]
            for r in (ra, rx)
        }
        d = {r: jbfs(r[1], m[r], home[r]) for r in (ra, rx)}
        alone = d[ra][home[ra]] + d[rx][home[rx]]

        best: tuple[int, int, int, int, int, int] | None = None
        for first, second in ((ra, rx), (rx, ra)):
            G = parity(M, home[first])
            d2 = jbfs(home[first], m[second], home[second])
            if d2[home[second]] >= INF:
                continue
            for bottom, top in ((ra, rx), (rx, ra)):
                want = 0 if top == first else 1
                for c in range(N * N):
                    if c in nests or c == top[1] or h2[c] + M > MAX_H:
                        continue
                    cost = d[bottom][c] + d[top][c] + G[want][c]
                    if cost >= INF:
                        continue
                    save = alone - cost - d2[home[second]]
                    if save > 0 and (best is None or save > best[0]):
                        best = (
                            save, bottom[1], top[1], c, first[0], second[0]
                        )
        return best

    def _merge(self, bc: int, tc: int, c: int, kf: int, ks: int) -> None:
        """bottom (マス bc) と top (マス tc) をマス c で合流させ、巣 kf → 巣 ks と運ぶ。"""
        board = self.board
        N = board.N
        nests = {i * N + j for i, j in board.nests}
        hf = board.nests[kf][0] * N + board.nests[kf][1]
        hs = board.nests[ks][0] * N + board.nests[ks][1]
        top_color = board.top_color(tc // N, tc % N)
        M = board.height(bc // N, bc % N) + board.height(tc // N, tc % N)
        for x in (bc, tc):
            col = board.top_color(x // N, x % N)
            home = board.nests[col][0] * N + board.nests[col][1]
            if x != c:
                ok = self._walk_to(x // N, x % N, c, home)
                assert ok, "合流地点へ届かない"
        h2 = self._heights()
        h2[c] -= M  # 合流した一団の下にいる分だけ残す
        avoid = nests - {hf}
        G = self._parity_dist(M, hf, h2, avoid)
        want = 0 if top_color == kf else 1
        self._walk_parity(c, M, hf, h2, avoid, G, want)
        assert board.top_color(hf // N, hf % N) == ks
        ok = self._walk_to(hf // N, hf % N, hs, hs)
        assert ok, "後の巣へ届かない"

    def _parity_edges(
        self,
        u: int,
        M: int,
        home: int,
        h: list[int],
        avoid: set[int],
    ) -> list[int]:
        """一団 (M 匹) がマス u に着地しているとき、1 手で着地できるマス。

        u の下には h[u] 匹いるので最大 h[u]+1 マス跳べる。着地後の高さが
        MAX_H を超えるマスと、avoid (他の色の巣) には着地しない。
        巣 home に着いたら帰巣して終わるので、home からは先へ進まない。
        """
        if u == home:
            return []
        res = []
        for ray in self.rays[u]:
            for v in ray[: h[u] + 1]:
                if v not in avoid and h[v] + M <= MAX_H:
                    res.append(v)
        return res

    def _parity_dist(
        self,
        M: int,
        home: int,
        h: list[int],
        avoid: set[int],
    ) -> list[list[int]]:
        """各マスから巣 home まで、手数の偶奇を指定したときの最小手数を求める。

        一団 (M 匹) がマス u に着地している状態から、ちょうど偶数手 (p=0)
        または奇数手 (p=1) で home に着く最小手数を G[p][u] とする。
        home から逆向きに BFS して、全マス分をまとめて求める。
        偶奇を合わせるために、同じマスを行き来する経路も許す。

        Returns:
            G[p][u] (届かなければ INF)。
        """
        board = self.board
        N = board.N
        radj: list[list[int]] = [[] for _ in range(N * N)]
        for u in range(N * N):
            if board.is_floor(u // N, u % N):
                for v in self._parity_edges(u, M, home, h, avoid):
                    radj[v].append(u)
        G = [[INF] * (N * N) for _ in range(2)]
        G[0][home] = 0
        q = [(home, 0)]
        for v, p in q:
            for u in radj[v]:
                if G[p ^ 1][u] == INF:
                    G[p ^ 1][u] = G[p][v] + 1
                    q.append((u, p ^ 1))
        return G

    def _walk_parity(
        self,
        c: int,
        M: int,
        home: int,
        h: list[int],
        avoid: set[int],
        G: list[list[int]],
        want: int,
    ) -> None:
        """マス c に着地している一団 (M 匹) を、偶奇 want の手数で巣 home へ運ぶ。"""
        board = self.board
        N = board.N
        assert G[want][c] < INF, "偶奇を合わせた経路がない"
        u, p = c, want
        while u != home:
            for v in self._parity_edges(u, M, home, h, avoid):
                if G[p ^ 1][v] == G[p][u] - 1:
                    break
            else:
                assert False, "偶数手の経路をたどれない"
            self._jump_cells(u, v, M)
            u, p = v, p ^ 1
        assert board.top_color(home // N, home % N) != board.nest[home // N][
            home % N
        ]

    def _jump_cells(self, c: int, n: int, M: int) -> None:
        """マス c の上 M 匹を、同じ行か列のマス n へ跳ばす。"""
        board = self.board
        N = board.N
        di, dj = n // N - c // N, n % N - c % N
        ln = abs(di) + abs(dj)
        ci, cj = divmod(c, N)
        d = DIR_OF[(di // ln, dj // ln)]
        board.jump(ci, cj, board.height(ci, cj) - M, d, ln)

    def _heights(self) -> list[int]:
        """今の盤面の各マスの塔の高さ。"""
        board = self.board
        return [
            board.height(i, j) for i in range(board.N) for j in range(board.N)
        ]

    def _jump_bfs(
        self,
        s: int,
        m: int,
        home: int,
        h: list[int],
    ) -> tuple[list[int], list[int]]:
        """マス s の一団 (m 匹) を動かすときの、各マスまでの最小手数を求める。

        一団が高さ b のマスに着地すると、次はそこから同じ方向に最大 b+1 マス
        跳べる (出発点 s では下に誰もいないので 1 マス)。1 手のコストは
        どれも 1 なので、普通の BFS で求まる。
        着地後の高さが MAX_H を超えるマスには着地しない。
        自分の巣 home に着地すると一団は帰巣するので、home からは先へ進まない。
        こうすると、home 以外へ向かう経路は home を通らない。

        Args:
            s: 出発点。
            m: 一団の匹数。
            home: 一団の色の巣。
            h: 各マスの塔の高さ (s には一団だけがいること)。

        Returns:
            (ds, prev): ds[c] はマス c までの最小手数 (届かなければ INF)、
            prev[c] は最短経路で c の直前に着地したマス。
        """
        ds = [INF] * len(h)
        prev = [-1] * len(h)
        ds[s] = 0
        q = [s]
        for c in q:
            if c == home:
                continue
            b = 0 if c == s else h[c]
            for ray in self.rays[c]:
                for n in ray[: b + 1]:
                    if ds[n] != INF or h[n] + m > MAX_H:
                        continue
                    ds[n] = ds[c] + 1
                    prev[n] = c
                    q.append(n)
        return ds, prev

    def _route(
        self,
        prev: list[int],
        s: int,
        t: int,
    ) -> list[tuple[str, int]]:
        """_jump_bfs の prev から、マス s から t までの手順を復元する。

        Returns:
            順に並べた (方向, 飛距離) のリスト。
        """
        N = self.board.N
        cells = [t]
        while cells[-1] != s:
            assert prev[cells[-1]] != -1
            cells.append(prev[cells[-1]])
        cells.reverse()
        res: list[tuple[str, int]] = []
        for c, n in zip(cells, cells[1:]):
            di, dj = n // N - c // N, n % N - c % N
            ln = abs(di) + abs(dj)
            res.append((DIR_OF[(di // ln, dj // ln)], ln))
        return res

    def _walk_to(self, i: int, j: int, t: int, home: int) -> bool:
        """(i,j) の一団を、今の盤面で手数が最小の経路でマス t まで動かす。

        一団のまま着地できるマスだけでは届かないときは、高い塔を
        分けて越える手 (_cross_route) も使って届く経路を探す。

        Args:
            i, j: 一団のいるマス。このマスには一団しかいないこと。
            t: 行き先。
            home: 一団の色の巣。

        Returns:
            動かせたら True。どうやっても届かなければ何もせず False。
        """
        board = self.board
        s = i * board.N + j
        m = board.height(i, j)
        h = self._heights()
        ds, prev = self._jump_bfs(s, m, home, h)
        if ds[t] != INF:
            for d, ln in self._route(prev, s, t):
                i, j = board.jump(i, j, board.height(i, j) - m, d, ln)
            return True

        route = self._cross_route(s, m, home, h, t)
        if route is None:
            return False
        for c, p, n in route:
            if p == -1:
                di, dj = self._delta(c, n)
                ln = abs(di) + abs(dj)
                d = DIR_OF[(di // ln, dj // ln)]
                ci, cj = divmod(c, board.N)
                board.jump(ci, cj, board.height(ci, cj) - m, d, ln)
            else:
                self._cross(c, p, n, m)
                self.crossings += 1
        return True

    def _delta(self, c: int, n: int) -> Pos:
        """マス c から n への変化量。"""
        N = self.board.N
        return n // N - c // N, n % N - c % N

    def _cross_route(
        self,
        s: int,
        m: int,
        home: int,
        h: list[int],
        t: int,
    ) -> list[tuple[int, int, int]] | None:
        """高い塔を分けて越える手も使って、マス s から t への経路を求める。

        一団 (m 匹) のままでは着地できない高さ g の塔 P (g+m > MAX_H) が
        隣にあるとき、一団を MAX_H-g 匹以下ずつに分けて P に乗せ、P を
        踏み台に (最大 g+1 マス) 先のマス L へ跳ばして再合流できる。
        分ける回数を p とすると 2p 手かかる。手数が 1 でない手が混ざるので、
        ダイクストラ法で求める。

        Args:
            s: 出発点。
            m: 一団の匹数。
            home: 一団の色の巣。_jump_bfs と同じく、home からは先へ進まない。
            h: 各マスの塔の高さ (s には一団だけがいること)。
            t: 行き先。

        Returns:
            順に並べた (出発点, 越える塔 (普通のジャンプなら -1), 着地点) の
            リスト。届かなければ None。
        """
        h = h[:]
        h[s] = 0  # 一団が出発したあとの s は空 (s を越える塔と見なさないため)
        ds = [INF] * len(h)
        prev: list[tuple[int, int]] = [(-1, -1)] * len(h)  # (直前のマス, 越える塔)
        ds[s] = 0
        pq = [(0, s)]
        while pq:
            dc, c = heapq.heappop(pq)
            if dc != ds[c]:
                continue
            if c == t:
                break
            if c == home:
                continue
            b = 0 if c == s else h[c]
            for ray in self.rays[c]:
                # 普通のジャンプ
                for n in ray[: b + 1]:
                    if h[n] + m <= MAX_H and dc + 1 < ds[n]:
                        ds[n] = dc + 1
                        prev[n] = (c, -1)
                        heapq.heappush(pq, (dc + 1, n))
                # 隣の高い塔 P を分けて越える
                if not ray:
                    continue
                P = ray[0]
                g = h[P]
                if g + m <= MAX_H or g >= MAX_H:
                    continue
                cost = dc + 2 * -(-m // (MAX_H - g))
                for ray2 in self.rays[P]:
                    for n in ray2[: g + 1]:
                        if n != c and h[n] + m <= MAX_H and cost < ds[n]:
                            ds[n] = cost
                            prev[n] = (c, P)
                            heapq.heappush(pq, (cost, n))
        if ds[t] == INF:
            return None
        route: list[tuple[int, int, int]] = []
        n = t
        while n != s:
            c, P = prev[n]
            route.append((c, P, n))
            n = c
        return route[::-1]

    def _cross(self, c: int, P: int, L: int, m: int) -> None:
        """マス c の一団 (上 m 匹) を、隣の塔 P を分けて越えさせ、L で再合流させる。

        一団の上から、P に乗れるだけ (MAX_H - P の高さ) ずつ P に乗せ、
        P を踏み台に L へ跳ばす。これを一団がいなくなるまで繰り返す。
        """
        board = self.board
        N = board.N
        ci, cj = divmod(c, N)
        pi, pj = divmod(P, N)
        di, dj = self._delta(c, P)
        d1 = DIR_OF[(di, dj)]
        di, dj = self._delta(P, L)
        ln = abs(di) + abs(dj)
        d2 = DIR_OF[(di // ln, dj // ln)]
        g = board.height(pi, pj)
        rest = m
        while rest:
            a = min(rest, MAX_H - g)
            board.jump(ci, cj, board.height(ci, cj) - a, d1, 1)
            board.jump(pi, pj, g, d2, ln)
            rest -= a

    # ---- 乗り先の決定 (見積もりと実際の運び方で共通) ----

    @staticmethod
    def _root_of(par: list[int], x: int) -> int:
        """乗り先を根 (巣へ直行するスライム) までたどる。"""
        while par[x] != -1:
            x = par[x]
        return x

    def _plan_rides(
        self,
        k: int,
        dist_from: Callable[[int, int], list[int]],
    ) -> tuple[list[Slime], list[int]]:
        """色 k の各スライムを、巣へ直行させるか、別のスライムに乗せるかを決める。

        巣に近い順に判断し、乗り先の候補は判断済み (自分より巣に近い) の同色
        スライムに限る。こうすると乗り先が循環せず、乗ってくる側は必ず自分より
        後の番号になる。最も近い候補までの手数が巣までの手数より少なく、乗っても
        根の塔の高さが build_h 以下なら乗る。そうでなければ巣へ直行する。

        Args:
            k: 色。
            dist_from: dist_from(i, j)[c] は (i,j) からマス c までの手数。

        Returns:
            (q, par):
            q[x] は x 番目のスライムの (巣までの距離, i, j) で、巣に近い順。
            par[x] は乗り先の番号 (-1 なら巣へ直行)。
        """
        board = self.board
        N = board.N
        home = board.nests[k][0] * N + board.nests[k][1]
        q: list[Slime] = []
        for i in range(N):
            for j in range(N):
                if board.top_color(i, j) == k:
                    q.append((board.dist[k][i][j], i, j))
        q.sort()

        par = [-1] * len(q)
        size = [1] * len(q)  # 最終的な塔の高さ (自分 + 乗ってくる数)
        for x, (_, i, j) in enumerate(q):
            ds = dist_from(i, j)
            y = -1  # 判断済みの中で最も近いスライム
            for z in range(x):
                _, zi, zj = q[z]
                if y == -1 or ds[zi * N + zj] < ds[q[y][1] * N + q[y][2]]:
                    y = z
            if y == -1:
                continue
            _, yi, yj = q[y]
            if ds[yi * N + yj] >= ds[home]:
                continue
            # 乗ると、乗り先から根までのすべての塔が 1 高くなる。最も高いのは根。
            if size[self._root_of(par, y)] + 1 > self.build_h:
                continue
            par[x] = y
            r = y
            while r != -1:
                size[r] += 1
                r = par[r]
        return q, par

    def _move_order(self, par: list[int]) -> list[tuple[int, int]]:
        """_plan_rides の結果から、一団を動かす順番を決める。

        塔は一つずつ組み上げて巣へ運ぶ。こうすると他のマスは未着手
        (高さ 1 以下) のままなので、運ぶ途中で完成済みの塔の上に着地して
        高さが MAX_H を超えることがない。

        Returns:
            動かす順に並べた (スライムの番号, 行き先の番号) のリスト。
            行き先が -1 なら巣。
        """
        res: list[tuple[int, int]] = []
        for x in range(len(par)):
            if par[x] != -1:
                continue
            # x を根とする塔のメンバー (乗ってくるのは x より後の番号だけ)
            mem = [
                z for z in range(x + 1, len(par)) if self._root_of(par, z) == x
            ]
            # 後の番号から動かす。乗り先は自分より前の番号なので、
            # 自分に乗ってくる仲間は自分が動く時点で到着済みになる。
            for z in reversed(mem):
                res.append((z, par[z]))
            # 組み上がった塔を根ごと巣へ運ぶ
            res.append((x, -1))
        return res

    # ---- 色の順番の見積もり ----

    def _plan_walks(self, k: int) -> list[Walk]:
        """色の順番を決めるために、色 k の運び方を見積もる。

        他の色が全員残っている (初期状態の) 盤面で、_carry と同じく踏み台を
        考慮して乗り先と経路を決める。盤面は動かさず、高さだけを追う。

        Returns:
            動かす順に並べた一団の移動 (i, j, 手順) のリスト。
            手順は (方向, 飛距離) のリスト。
        """
        board = self.board
        N = board.N
        home = board.nests[k][0] * N + board.nests[k][1]
        h = self._heights()
        q, par = self._plan_rides(
            k, lambda i, j: self._jump_bfs(i * N + j, 1, home, h)[0]
        )
        walks: list[Walk] = []
        for x, y in self._move_order(par):
            _, i, j = q[x]
            s = i * N + j
            t = home if y == -1 else q[y][1] * N + q[y][2]
            m = h[s]
            _, prev = self._jump_bfs(s, m, home, h)
            walks.append((i, j, self._route(prev, s, t)))
            h[s] -= m
            h[t] += m
            if t == home:
                h[t] -= m  # 巣に着いた一団は帰巣する
        return walks

    def _decide_order(self, walks: list[list[Walk]]) -> tuple[list[int], int]:
        """色を処理する順番を、合計の操作回数が最小になるよう bit DP で決める。

        色 k を処理するとき、盤面にあるのは色 k と未処理の色のスライム
        (初期位置に 1 匹ずつ) だけ。処理済みの色は全員帰巣している。
        そのため色 k の操作回数は「処理済みの色の集合 S」だけで決まり、
        dp[S] = S を処理し終えるまでの最小操作回数 で最適な順番が求まる。

        Args:
            walks: walks[k] は色 k の _plan_walks の結果。

        Returns:
            (順番, 予想される操作回数の合計)。
        """
        board = self.board
        N, K = board.N, board.K
        # color[c]: 初期状態でマス c (= i*N+j) にいるスライムの色 (いなければ -1)
        color = [board.top_color(i, j) for i in range(N) for j in range(N)]

        # paths[k]: 色 k の各移動の (出発点, 各ジャンプで通るマスの列, 巣へ運ぶか)
        paths: list[list[tuple[int, list[list[int]], bool]]] = []
        # rel[k]: 色 k の経路上にいる他の色の集合。
        # 色 k の操作回数に効くのはこれらの色が処理済みかどうかだけ。
        rel = [0] * K
        for k in range(K):
            ps = []
            home = board.nests[k][0] * N + board.nests[k][1]
            for i, j, moves in walks[k]:
                s = i * N + j
                segs = []
                for d, ln in moves:
                    di, dj = DIRS[d]
                    seg = []
                    for _ in range(ln):
                        i, j = i + di, j + dj
                        seg.append(i * N + j)
                    segs.append(seg)
                    for c in seg:
                        if color[c] != -1 and color[c] != k:
                            rel[k] |= 1 << color[c]
                ps.append((s, segs, segs[-1][-1] == home))
            paths.append(ps)

        memo: list[dict[int, int]] = [{} for _ in range(K)]

        def cost(k: int, S: int) -> int:
            """処理済みの色の集合が S のとき、色 k の操作回数。"""
            key = S & rel[k]
            if key in memo[k]:
                return memo[k][key]
            # 盤面をコピーせず、動いたマスの高さだけを h に持って数える。
            h: dict[int, int] = {}

            def height(c: int) -> int:
                if c in h:
                    return h[c]
                col = color[c]
                return int(col == k or (col != -1 and not key >> col & 1))

            # 各ジャンプは、踏み台 (下の匹数) が足りればそのまま 1 手で跳ぶ。
            # 足りなければ、同じ向きに跳べるだけ跳ぶのを繰り返す。
            ops = 0
            for s, segs, to_home in paths[k]:
                m = height(s)
                cur = s
                for seg in segs:
                    p = 0
                    while p < len(seg):
                        hc = height(cur)
                        p += min(hc - m + 1, len(seg) - p)
                        h[cur] = hc - m
                        cur = seg[p - 1]
                        h[cur] = height(cur) + m
                        ops += 1
                if to_home:
                    h[cur] -= m  # 巣に着いた一団は帰巣する
            memo[k][key] = ops
            return ops

        full = (1 << K) - 1
        dp = [INF] * (1 << K)
        prev = [-1] * (1 << K)  # dp[S] を達成したときに最後に処理した色
        dp[0] = 0
        for S in range(1 << K):
            if dp[S] == INF:
                continue
            for k in range(K):
                if S >> k & 1:
                    continue
                v = dp[S] + cost(k, S)
                if v < dp[S | 1 << k]:
                    dp[S | 1 << k] = v
                    prev[S | 1 << k] = k

        order: list[int] = []
        S = full
        while S:
            order.append(prev[S])
            S ^= 1 << prev[S]
        return order[::-1], dp[full]


class BusSolver(Solver):
    """1 つの塔 (バス) が盤面を巡回しながらスライムを拾い、巣を回って降ろす。

    バスの盤面上の積み順を、下から上への色の列 S で持つ。
    - 移動: 1 手ごとにバス全体が上下反転する。L 手移動すると、L が偶数なら
      S のまま、奇数なら反転した並び S_L になる。
    - 拾う: 1 匹だけいるマス X に着地すると、X が一番下に入り
      (S ← [X] + S_L)、以後は下に何も残さず跳ぶので X ごと運べる。
    - 降ろす: 巣 c に着地すると、S_L の上から続く色 c が帰巣する。
    同じ色は常に 1 つの塊にしておく (巣に着いたとき、その色がまとめて
    帰巣するように)。どの色が上に来るか、拾った色がどちらの端に付くかは
    移動の手数の偶奇で決まるので、偶奇ごとの最小手数を BFS で求めて選ぶ。

    バスが乗せるのは「今運んでいる色 (cur)」と「次に運ぶ色 (next)」の
    2 色まで (連鎖方式)。cur は盤面に残っている分を近い順に全部拾ってから
    cur の巣へ向かい、next はバスから radius 手以内にあるものだけ
    ついでに拾う。cur を降ろしたら next が新しい cur になる。

    公開するのは solve だけ (Solver の部品を使い回す)。
    """

    def __init__(self, board: Board, radius: int) -> None:
        super().__init__(board)
        self.radius = radius  # next の色をついでに拾う距離 (手数) の上限
        # バスが拾ってよい色 (None ならすべて)
        self.allowed: set[int] | None = None
        self.n_bus = 0  # 出したバスの数 (確認用)
        self.n_split = 0  # 行き詰まって切り離した回数 (確認用)

    def solve(self) -> None:
        """全スライムを巣へ返す操作を board.ops に積む。

        盤面が空になるまでバスを出す。バスはいつも、残っているスライムの
        うち自分の巣から最も遠いものから出発する (出発にコストはかからない)。
        """
        board = self.board
        N = board.N
        while True:
            cells = [
                c for c in range(N * N)
                if board.height(c // N, c % N) > 0
            ]
            if not cells:
                break

            def far(c: int) -> int:
                col = board.top_color(c // N, c % N)
                return -board.dist[col][c // N][c % N]

            self._run_bus(min(cells, key=far))
            self.n_bus += 1
        print(
            f"bus: radius={self.radius} ops={len(board.ops)} "
            f"buses={self.n_bus} splits={self.n_split}",
            file=sys.stderr,
        )

    # ---- ルートを計画するバス (ペアの 2 色) ----

    def _planned_pair(self, k: int, p: int) -> None:
        """色 k と p のスライムを、ルートを計画したバスで巣へ運ぶ。"""
        self._planned([k, p], PLAN_ITERS)

    def _planned(self, colors: list[int], iters: int) -> None:
        """colors の色のスライムを、ルートを計画したバスで巣へ運ぶ。

        1. ルートを「拾うスライムの順番」の列で表し、ところどころに「色 c を
           降ろす」目印 (-1 - c) を入れる。列をルートに読み替える決まりは
           _decode (バスに乗せる色は 2 色まで)。手数は各地点間の歩数
           (踏み台・偶奇は無視) で見積もる。
        2. 最初の列は、色ごとに巣から最も遠いスライムから近い順に並べ、
           色の順番は巣どうしが近い順につなぐ。局所探索 (区間の反転・
           1 つの移動・目印の追加と削除、改善か同点なら採用) で短くする。
           乱数の種は固定し、iters 回で打ち切る。
        3. 計画の順番で、偶奇つき BFS で 1 区間ずつ実際に動かす
           (_run_plan)。拾えずに残ったスライムは連鎖バスで片付ける。
        """
        board = self.board
        N = board.N
        nests = {i * N + j for i, j in board.nests}
        slimes = [
            c for c in range(N * N)
            if c not in nests and board.height(c // N, c % N) == 1
            and board.top_color(c // N, c % N) in colors
        ]
        if not slimes:
            return
        color = {c: board.top_color(c // N, c % N) for c in slimes}
        home = {
            x: board.nests[x][0] * N + board.nests[x][1] for x in colors
        }
        # dist2[a][p][b]: 地点 a (スライムか巣) から b まで、偶奇 p の手数で
        # 着く最小手数。今の盤面のスライムを踏み台にした偶奇つき BFS で
        # 求める (途中で拾われて踏み台が消える分は無視する近似)。
        # dist[a][b]: 偶奇を問わない最小手数 (最初の列を作るのに使う)。
        h = self._heights()
        dist2: dict[int, list[list[int]]] = {}
        dist: dict[int, list[int]] = {}
        for a in slimes + list(home.values()):
            ha, h[a] = h[a], 0  # a にいるのはバス自身
            dist2[a] = self._bus_bfs(a, 1, h, set())[0]
            h[a] = ha
            dist[a] = [min(x, y) for x, y in zip(*dist2[a])]

        # 最初の列: 色ごとに巣から遠いスライムから近い順。色の順番は、
        # 最も遠いスライムを持つ色から始め、巣どうしが近い順につなぐ。
        by_color: dict[int, list[int]] = {}
        for c in slimes:
            by_color.setdefault(color[c], []).append(c)
        first = max(slimes, key=lambda c: dist[home[color[c]]][c])
        order = [color[first]]
        while len(order) < len(by_color):
            last = home[order[-1]]
            order.append(min(
                (x for x in by_color if x not in order),
                key=lambda x: dist[last][home[x]],
            ))
        seq: list[int] = []
        for x in order:
            rest = set(by_color[x])
            cur = max(rest, key=lambda c: dist[home[x]][c])
            seq.append(cur)
            rest.discard(cur)
            while rest:
                cur = min(rest, key=lambda c: dist[cur][c])
                seq.append(cur)
                rest.discard(cur)

        best_cost = self._decode(seq, color, home, dist2)[0]
        rng = random.Random(0)
        for _ in range(iters):
            cand = seq[:]
            move = rng.randrange(4)
            n = len(cand)
            if move == 0 and n >= 2:  # 区間の反転
                i, j = sorted(rng.sample(range(n), 2))
                cand[i:j + 1] = cand[i:j + 1][::-1]
            elif move == 1 and n >= 2:  # 1 つを別の位置へ
                x = cand.pop(rng.randrange(n))
                cand.insert(rng.randrange(n), x)
            elif move == 2:  # 降ろす目印を追加
                cand.insert(rng.randrange(n + 1), -1 - rng.choice(colors))
            else:  # 降ろす目印を削除
                marks = [i for i, x in enumerate(cand) if x < 0]
                if not marks:
                    continue
                cand.pop(rng.choice(marks))
            cost = self._decode(cand, color, home, dist2)[0]
            if cost <= best_cost:
                seq, best_cost = cand, cost

        self._run_plan(self._decode(seq, color, home, dist2)[1])
        self._sweep_colors(set(colors))

    def _plan_setup(
        self,
        colors: list[int],
    ) -> tuple[
        list[int], dict[int, int], dict[int, int],
        dict[int, list[list[int]]], dict[int, list[int]],
    ]:
        """計画の準備: 対象のスライム、色、巣、地点間の手数の表を作る。

        Returns:
            (スライムのマスのリスト, 色, 巣, dist2, dist)。dist2 と dist は
            _planned と同じ (偶奇別 / 偶奇を問わない最小手数)。
        """
        board = self.board
        N = board.N
        nests = {i * N + j for i, j in board.nests}
        slimes = [
            c for c in range(N * N)
            if c not in nests and board.height(c // N, c % N) == 1
            and board.top_color(c // N, c % N) in colors
        ]
        color = {c: board.top_color(c // N, c % N) for c in slimes}
        home = {
            x: board.nests[x][0] * N + board.nests[x][1] for x in colors
        }
        h = self._heights()
        dist2: dict[int, list[list[int]]] = {}
        dist: dict[int, list[int]] = {}
        for a in slimes + list(home.values()):
            ha, h[a] = h[a], 0  # a にいるのはバス自身
            dist2[a] = self._bus_bfs(a, 1, h, set())[0]
            h[a] = ha
            dist[a] = [min(x, y) for x, y in zip(*dist2[a])]
        return slimes, color, home, dist2, dist

    def _planned_sa(self, colors: list[int], limit: float) -> None:
        """colors の色のスライムを、焼きなまし法で計画したバスで運ぶ。

        ルートを「バスごとの拾う順番の列」の集まりで表す。各バスは空から
        始まって空で終わるので、全体の手数は各バスの手数 (_decode) の和。
        1 つの変更で影響を受けるバスは 1〜2 台なので、そのバスだけ
        計算し直す。変更の種類:
        - バスの中: 1 つの移動 / 区間の反転 / 降ろす目印の追加・削除
        - バスの間: スライムを別のバスへ移す / 2 台の間で入れ替える /
          バスを分ける / 2 台をつなぐ
        悪くなる変更も温度に応じた確率で受け入れ、温度は時間とともに下げる。
        最初の解は、色ごとに巣から遠い順→近い順に並べ、BUS_CAP 匹ずつ
        バスに分けたもの。最後に最良の解を実際に動かす (_run_plan)。

        Args:
            colors: 対象の色。
            limit: 焼きなまし法に使う時間 (秒)。
        """
        slimes, color, home, dist2, dist = self._plan_setup(colors)
        if not slimes:
            return

        # 最初の解: 色ごとに遠い順→近い順、BUS_CAP 匹ずつ
        trips: list[list[int]] = []
        for x in colors:
            rest = {c for c in slimes if color[c] == x}
            if not rest:
                continue
            cur = max(rest, key=lambda c: dist[home[x]][c])
            order = [cur]
            rest.discard(cur)
            while rest:
                cur = min(rest, key=lambda c: dist[cur][c])
                order.append(cur)
                rest.discard(cur)
            for i in range(0, len(order), BUS_CAP):
                trips.append(order[i:i + BUS_CAP])

        def cost_of(t: list[int]) -> int:
            return self._decode(t, color, home, dist2)[0] if t else 0

        costs = [cost_of(t) for t in trips]
        total = sum(costs)
        best_total, best = total, [t[:] for t in trips]
        rng = random.Random(0)
        start = time.perf_counter()
        T0, T1 = 2.0, 0.05
        temp = T0
        it = 0
        while True:
            if it & 63 == 0:
                el = (time.perf_counter() - start) / limit
                if el >= 1:
                    break
                temp = T0 * (T1 / T0) ** el
            it += 1
            n = len(trips)
            i = rng.randrange(n)
            ti = trips[i]
            move = rng.randrange(8)
            j = -1
            if move == 0 and len(ti) >= 2:  # バスの中で 1 つを移動
                a = ti[:]
                x = a.pop(rng.randrange(len(a)))
                a.insert(rng.randrange(len(a) + 1), x)
                new = [(i, a)]
            elif move == 1 and len(ti) >= 2:  # バスの中で区間の反転
                a = ti[:]
                p, q = sorted(rng.sample(range(len(a)), 2))
                a[p:q + 1] = a[p:q + 1][::-1]
                new = [(i, a)]
            elif move == 2 and n >= 2:  # 別のバスへ移す
                j = rng.randrange(n - 1)
                j += j >= i
                a, b = ti[:], trips[j][:]
                x = a.pop(rng.randrange(len(a)))
                b.insert(rng.randrange(len(b) + 1), x)
                new = [(i, a), (j, b)]
            elif move == 3 and n >= 2:  # 2 台の間で入れ替える
                j = rng.randrange(n - 1)
                j += j >= i
                a, b = ti[:], trips[j][:]
                p, q = rng.randrange(len(a)), rng.randrange(len(b))
                a[p], b[q] = b[q], a[p]
                new = [(i, a), (j, b)]
            elif move == 4 and len(ti) >= 2:  # バスを分ける
                p = rng.randrange(1, len(ti))
                new = [(i, ti[:p]), (n, ti[p:])]
            elif move == 5 and n >= 2:  # 2 台をつなぐ
                j = rng.randrange(n - 1)
                j += j >= i
                new = [(i, ti + trips[j]), (j, [])]
            elif move == 6:  # 降ろす目印を追加
                cs = [color[x] for x in ti if x >= 0]
                if not cs:
                    continue
                a = ti[:]
                a.insert(rng.randrange(len(a) + 1), -1 - rng.choice(cs))
                new = [(i, a)]
            elif move == 7:  # 降ろす目印を削除
                marks = [p for p, x in enumerate(ti) if x < 0]
                if not marks:
                    continue
                a = ti[:]
                a.pop(rng.choice(marks))
                new = [(i, a)]
            else:
                continue
            old = sum(costs[k] for k, _ in new if k < n)
            nc = [cost_of(t) for _, t in new]
            delta = sum(nc) - old
            if delta <= 0 or rng.random() < math.exp(-delta / temp):
                for (k, t), c in zip(new, nc):
                    if k < n:
                        trips[k], costs[k] = t, c
                    else:
                        trips.append(t)
                        costs.append(c)
                total += delta
                # 空になったバス (と目印だけのバス) を取り除く
                keep = [
                    k for k in range(len(trips))
                    if any(x >= 0 for x in trips[k])
                ]
                if len(keep) != len(trips):
                    trips = [trips[k] for k in keep]
                    costs = [costs[k] for k in keep]
                if total < best_total:
                    best_total, best = total, [t[:] for t in trips]

        events: list[tuple[int, int]] = []
        for t in best:
            events += self._decode(t, color, home, dist2)[1]
        self._run_plan(events)
        self._sweep_colors(set(colors))

    def _decode(
        self,
        seq: list[int],
        color: dict[int, int],
        home: dict[int, int],
        dist2: dict[int, list[list[int]]],
    ) -> tuple[int, list[tuple[int, int]]]:
        """計画の列を、実際に行う出来事の列に読み替え、手数を見積もる。

        - スライム X: 拾う。満杯 (BUS_CAP 匹) か、X の色が乗っておらず
          すでに 2 色乗っているなら、先に近いほうの巣で降ろす。
          バスが空なら、X から新しいバスを手数ゼロで出す。
        - 目印 -1 - c: 色 c が乗っていれば、色 c の巣で降ろす。
        - 最後に残った色は、近いほうの巣から順に降ろす。
        バスの中の並び S (下から上) を追い、各区間の手数は、並びの決まり
        (拾った色は一番下に入り、同じ色は 1 つの塊 / 降ろす色が一番上) を
        満たす偶奇の手数 dist2 から取る。塔全体は 1 手ごとに反転するので、
        偶数手なら S のまま、奇数手なら反転した並びで着く。
        決まりを満たす偶奇で着けないときは、罰の手数 PARITY_PENALTY を足す。

        Returns:
            (見積もりの手数, 出来事の列)。出来事は (0, X) が拾う、
            (1, c) が色 c を降ろす。
        """
        S: list[int] = []  # バスの中の並び (下から上)
        pos = -1  # バスがいるマス (-1 ならバスは空)
        cost = 0
        events: list[tuple[int, int]] = []

        def drop_cost(c: int) -> tuple[int, int]:
            """色 c を降ろすときの (手数, 偶奇)。"""
            # 着けなくても、c が上に来る向きで降ろしたことにする
            best = (INF, 0 if S[-1] == c else 1)
            for q in (0, 1):
                top = S[-1] if q == 0 else S[0]
                if top == c and dist2[pos][q][home[c]] < best[0]:
                    best = (dist2[pos][q][home[c]], q)
            return best

        def drop(c: int) -> None:
            nonlocal pos, cost, S
            d, q = drop_cost(c)
            cost += d if d < INF else PARITY_PENALTY
            SL = S if q == 0 else S[::-1]
            while SL and SL[-1] == c:
                SL = SL[:-1]
            S = SL
            pos = home[c] if S else -1
            events.append((1, c))

        def nearest_drop() -> None:
            drop(min(set(S), key=lambda c: drop_cost(c)[0]))

        for x in seq:
            if x < 0:
                if -1 - x in S:
                    drop(-1 - x)
                continue
            c = color[x]
            if len(S) >= BUS_CAP:
                nearest_drop()
            if S and c not in S and len(set(S)) >= 2:
                nearest_drop()
            if not S:
                S, pos = [c], x
                events.append((0, x))
                continue
            # 着けなくても、並びの決まりを満たす向きで拾ったことにする
            best = (INF, 1 if c == S[-1] else 0)
            for q in (0, 1):
                SL = S if q == 0 else S[::-1]
                if (c == SL[0] or c not in SL) and dist2[pos][q][x] < best[0]:
                    best = (dist2[pos][q][x], q)
            d, q = best
            cost += d if d < INF else PARITY_PENALTY
            S = [c] + (S if q == 0 else S[::-1])
            pos = x
            events.append((0, x))
        while S:
            nearest_drop()
        return cost, events

    def _run_plan(self, events: list[tuple[int, int]]) -> None:
        """_decode の出来事の列に沿って、バスを実際に動かす。

        拾う・降ろすの各区間は、偶奇つき BFS (_bus_bfs) で、並びの決まりを
        満たす偶奇のうち手数が少ないほうで動かす。偶奇が合わず拾えない
        スライムは飛ばす (あとで片付ける)。降ろせないときは、上の色の塊を
        切り離して巣へ運ぶ (_split_top)。
        """
        board = self.board
        N = board.N
        nest_of = [i * N + j for i, j in board.nests]
        pos = -1
        S: list[int] = []
        for kind, x in events:
            if kind == 0 and board.height(x // N, x % N) != 1:
                continue  # 先に別の手段で動いた
            if not S:
                if kind == 0:  # 新しいバスを出す
                    pos, S = x, [board.top_color(x // N, x % N)]
                continue
            m = len(S)
            h = self._heights()
            h[pos] -= m
            stop = {nest_of[c] for c in set(S)}
            D, prev = self._bus_bfs(pos, m, h, stop)
            if kind == 0:
                col = board.top_color(x // N, x % N)
                ok = [
                    q for q in (0, 1)
                    if D[q][x] < INF and m < BUS_CAP
                    and (col == (S if q == 0 else S[::-1])[0]
                         or col not in S)
                ]
                if not ok:
                    continue
                q = min(ok, key=lambda q: D[q][x])
                self._bus_move(pos, x, q, m, prev)
                S = [col] + (S if q == 0 else S[::-1])
                pos = x
            else:
                if x not in S:
                    continue
                t = nest_of[x]
                ok = [
                    q for q in (0, 1)
                    if D[q][t] < INF and (S if q == 0 else S[::-1])[-1] == x
                ]
                if not ok:
                    # 偶奇が合わない: 上の色の塊を切り離して巣へ運ぶ
                    S = self._split_top(pos, S)
                    if x in S:
                        S = self._split_top(pos, S)
                    continue
                q = min(ok, key=lambda q: D[q][t])
                self._bus_move(pos, t, q, m, prev)
                SL = S if q == 0 else S[::-1]
                while SL and SL[-1] == x:
                    SL = SL[:-1]
                S = SL
                pos = t
            assert board.height(pos // N, pos % N) == len(S)
        while S:  # 念のため残りを降ろす
            S = self._split_top(pos, S)

    def _sweep_colors(self, colors: set[int]) -> None:
        """colors の色だけを、連鎖方式のバスで巣へ運ぶ。

        バスが拾う色を colors に限る。colors の色のスライムが盤面から
        いなくなるまで、自分の巣から最も遠いものからバスを出す。
        """
        board = self.board
        N = board.N
        nests = {i * N + j for i, j in board.nests}
        self.allowed = colors
        while True:
            cells = [
                c for c in range(N * N)
                if c not in nests
                and board.height(c // N, c % N) == 1
                and board.top_color(c // N, c % N) in colors
            ]
            if not cells:
                break

            def far(c: int) -> int:
                col = board.top_color(c // N, c % N)
                return board.dist[col][c // N][c % N]

            self._run_bus(max(cells, key=far))
            self.n_bus += 1
        self.allowed = None

    def _sweep_color(self, k: int) -> None:
        """色 k だけを、バスで 1 色ずつ集めて巣へ運ぶ (radius=0 で使う)。

        色 k のスライムが盤面からいなくなるまで、自分の巣から最も遠い
        色 k のスライムからバスを出す。
        """
        board = self.board
        N = board.N
        ni, nj = board.nests[k]
        while True:
            cells = [
                c for c in range(N * N)
                if board.height(c // N, c % N) == 1
                and board.top_color(c // N, c % N) == k
                and (c // N, c % N) != (ni, nj)
            ]
            if not cells:
                break
            s = max(cells, key=lambda c: board.dist[k][c // N][c % N])
            self._run_bus(s)
            self.n_bus += 1

    def _run_bus(self, s: int) -> None:
        """マス s の 1 匹からバスを出し、空になるまで拾う・降ろすを繰り返す。

        各ステップで、今の位置から偶奇ごとの最小手数を求め (_bus_bfs)、
        次の候補の中で手数が最小のものを選ぶ。
        - cur の色を拾う: 盤面に残っていれば距離によらず候補。
        - next の色を拾う: radius 手以内のものだけ。next がまだ決まって
          いなければ、cur 以外のどの色でもよい (拾った色が next になる)。
        - cur の巣で降ろす: cur が盤面に残っていないか、バスが満杯か、
          cur を拾えないときだけ候補。着いたときに cur が上に来る偶奇にする。
        拾う候補は、拾ったあとも同じ色が 1 つの塊のままになるものに限る。
        候補がないとき (偶奇が合わず降ろせない) は、上の色の塊を
        切り離して巣へ運ぶ (_split_top)。
        """
        board = self.board
        N = board.N
        nest_of = [i * N + j for i, j in board.nests]
        nests = set(nest_of)
        pos = s
        cur = board.top_color(s // N, s % N)
        nxt = -1
        S = [cur]
        while S:
            m = len(S)
            h = self._heights()
            h[pos] -= m  # バスの下 (出発点には誰もいない)
            # バスに乗っている色の巣だけは通り抜けない (着地すると帰巣が
            # 起きうる)。乗っていない色の巣は、着地しても何も起きない。
            stop = {nest_of[c] for c in set(S)}
            D, prev = self._bus_bfs(pos, m, h, stop)
            left = [
                c for c in range(N * N)
                if c not in nests and h[c] == 1
                and board.top_color(c // N, c % N) == cur
            ]
            picks: list[tuple[int, int, int]] = []  # (手数, 行き先, 偶奇)
            for p in (0, 1):
                SL = S if p == 0 else S[::-1]
                if m >= BUS_CAP:
                    break
                for c in range(N * N):
                    if D[p][c] >= INF or c in nests or h[c] != 1:
                        continue
                    col = board.top_color(c // N, c % N)
                    if col != cur:
                        if nxt not in (-1, col) or D[p][c] > self.radius:
                            continue
                        allowed = self.allowed
                        if allowed is not None and col not in allowed:
                            continue
                    if col != SL[0] and col in SL:
                        continue
                    picks.append((D[p][c], c, p))
            best = min(picks) if picks else None
            can_pick_cur = any(
                board.top_color(c // N, c % N) == cur for _, c, _ in picks
            )
            if not left or m >= BUS_CAP or not can_pick_cur:
                for p in (0, 1):
                    SL = S if p == 0 else S[::-1]
                    t = nest_of[cur]
                    if SL[-1] != cur or D[p][t] >= INF:
                        continue
                    if best is None or D[p][t] < best[0]:
                        best = (D[p][t], t, p)
            if best is None:
                S = self._split_top(pos, S)
                if S:
                    cur, nxt = S[-1], -1
                continue

            _, t, p = best
            # 拾うスライムの色は、着地する前に読む (着地後の一番上はバス)
            picked = board.top_color(t // N, t % N)
            self._bus_move(pos, t, p, m, prev)
            SL = S if p == 0 else S[::-1]
            if t in nests:
                while SL and SL[-1] == cur:
                    SL = SL[:-1]
                S = SL
                if S:
                    cur, nxt = S[-1], -1
            else:
                S = [picked] + SL
                if picked != cur:
                    nxt = picked
            pos = t
            assert board.height(pos // N, pos % N) == len(S)

    def _bus_bfs(
        self,
        s: int,
        m: int,
        h: list[int],
        nests: set[int],
        b0: int = 0,
    ) -> tuple[list[list[int]], list[list[int]]]:
        """マス s のバス (m 匹) から各マスへ、偶奇ごとの最小手数を求める。

        着地したマスの下に b 匹いれば、次は最大 b+1 マス跳べる (s では b0)。
        着地後の高さが MAX_H を超えるマスには着地しない。nests (バスに
        乗っている色の巣) に着地すると帰巣が起きうるので、行き先としてだけ
        扱い、そこから先へは進まない。

        Returns:
            (D, prev): D[p][v] は偶奇 p の手数で v に着く最小手数、
            prev[p][v] はその直前に着地したマス (直前の偶奇は p ^ 1)。
        """
        D = [[INF] * len(h) for _ in range(2)]
        prev = [[-1] * len(h) for _ in range(2)]
        D[0][s] = 0
        q = [(s, 0)]
        for u, p in q:
            if u != s and u in nests:
                continue
            b = b0 if u == s else h[u]
            for ray in self.rays[u]:
                for v in ray[: b + 1]:
                    if h[v] + m > MAX_H or D[p ^ 1][v] != INF:
                        continue
                    D[p ^ 1][v] = D[p][u] + 1
                    prev[p ^ 1][v] = u
                    q.append((v, p ^ 1))
        return D, prev

    def _bus_move(
        self,
        s: int,
        t: int,
        p: int,
        m: int,
        prev: list[list[int]],
    ) -> None:
        """_bus_bfs の結果に沿って、上 m 匹を s から偶奇 p の手数で t へ運ぶ。"""
        cells = [t]
        q = p
        while not (cells[-1] == s and q == 0):
            u = prev[q][cells[-1]]
            assert u != -1
            cells.append(u)
            q ^= 1
        cells.reverse()
        for c, n in zip(cells, cells[1:]):
            self._jump_cells(c, n, m)

    def _split_top(self, pos: int, S: list[int]) -> list[int]:
        """上の色の塊だけを、残りのバスを踏み台にして巣へ運ぶ。

        塊は 1 色だけなので、偶奇に関係なく巣に着けば帰巣する。
        残りのバスはその場に残る。

        Returns:
            残ったバスの列。
        """
        board = self.board
        N = board.N
        col = S[-1]
        b = 0
        while b < len(S) and S[-1 - b] == col:
            b += 1
        home = board.nests[col][0] * N + board.nests[col][1]
        h = self._heights()
        h[pos] -= b  # 塊の下には残りのバスがいる
        D, prev = self._bus_bfs(pos, b, h, {home}, h[pos])
        p = 0 if D[0][home] <= D[1][home] else 1
        assert D[p][home] < INF, "切り離した塊を巣へ運べない"
        self._bus_move(pos, home, p, b, prev)
        self.n_split += 1
        return S[:-b]


def search(N: int, K: int, C: list[str], start: float) -> Board:
    """パラメータを変えた案を時間の許す限り試し、スコアが最も良い盤面を返す。

    案ごとに盤面を作り直して最後まで解く。それまでの 1 案あたりの最長時間を
    見て、次の案が TIME_LIMIT までに終わりそうにないときは打ち切る。

    Args:
        N, K, C: 入力。
        start: プログラムの開始時刻 (time.perf_counter())。

    Returns:
        スコアが最も良かった案の盤面。
    """
    best: Board | None = None
    longest = 0.0
    # 色順 DP は重いので、最初の木の案で求めた色の順番を他の木の案でも
    # 使い回す (BUILD_H による違いは小さいとみなす)。ペアは案ごとに決める。
    plan: Plan | None = None
    for kind, param in CANDIDATES:
        t0 = time.perf_counter()
        if best is not None and t0 - start + longest > TIME_LIMIT:
            break
        board = Board(N, K, C)
        try:
            if kind == "tree":
                solver: Solver = Solver(board, param, plan)
                solver.solve()
            elif kind == "bus":
                solver = BusSolver(board, param)
                solver.solve()
            else:
                solver = BusSolver(board, INF)
                solver._planned_sa(list(range(K)), PLAN_TIME_ALL)
            if kind == "tree" and plan is None:
                plan = solver.plan
            # Solver は色ごとに盤面を複製して良いほうに差し替えるので、
            # 最後に solver が持っている盤面を使う
            board = solver.board
        except Exception as e:
            # 1 つの案が失敗しても、他の案の結果で答えられるようにする
            print(f"{kind}={param} failed: {e!r}", file=sys.stderr)
            continue
        finally:
            longest = max(longest, time.perf_counter() - t0)
        print(f"{kind}={param} score={board.score()}", file=sys.stderr)
        if best is None or board.score() < best.score():
            best = board
    assert best is not None
    return best


# ============================================================
# 実行
# ============================================================
start = time.perf_counter()
N, K = map(int, input().split())
C = [input() for _ in range(N)]

board = search(N, K, C, start)

print("\n".join(board.ops))
