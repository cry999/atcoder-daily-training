from typing import Generator
import os
import sys


DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


T = int(input())


for _ in range(T):
    N = int(input())
    S = input()

    CUM = [(S[0], 1)]
    cnt_0, cnt_1 = S[0] == '0', S[0] == '1'
    for c in S[1:]:
        pc, pn = CUM[-1]
        cnt_0, cnt_1 = cnt_0 + (c == '0'), cnt_1 + (c == '1')
        if pc == c:
            CUM[-1] = (c, pn+1)
        else:
            CUM.append((c, 1))

    # max_seq で空配列は操作しないように。
    CUM.append(('0', 0)), CUM.append(('1', 0))
    # debug(f'---{S=}---')
    # debug(f'{CUM=}')

    def max_seq(c: str) -> Generator[int, None, None]:
        return max(map(lambda x: x[1], filter(lambda x: x[0] == c, CUM)))

    max_seq_0 = max_seq('0')
    max_seq_1 = max_seq('1')

    debug(f'{cnt_0=}, {max_seq_0=}')
    debug(f'{cnt_1=}, {max_seq_1=}')

    ans = min(
        cnt_1 + 2*(cnt_0-max_seq_0),
        cnt_0 + 2*(cnt_1-max_seq_1),
    )
    print(ans)
