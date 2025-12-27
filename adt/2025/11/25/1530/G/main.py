from itertools import permutations


N, M = map(int, input().split())
S = [input() for _ in range(N)]
sum_len_s = sum(map(len, S))
T = set([input() for _ in range(M)])

underbars = ['_' * i for i in range(16)]


def dfs(n: int, d: int):
    '''要素数 n で、各要素が 1 つ以上の '_' で構成される配列を生成する。
    '_' の数は d 以下とする。
    '''
    if n == 0:
        return
    if n == 1:
        for nd in range(1, d+1):
            yield [underbars[nd]]
        return
    for nd in range(1, d-n+2):
        for a in dfs(n-1, d-nd):
            yield [underbars[nd]] + a
    return


def build(a: list[str], b: list[str]) -> str:
    return ''.join(
        b[i//2] if i % 2 else a[i//2]
        for i in range(len(a) + len(b))
    )


if N == 1:
    if S[0] in T or not (3 <= len(S[0]) <= 16):
        print(-1)
    else:
        print(S[0])
else:
    for perm in permutations(S):
        # d: '_' の総数
        d = 16 - sum_len_s
        for b in dfs(N-1, d):
            s = build(perm, b)
            if s not in T:
                print(s)
                exit()
    print(-1)
