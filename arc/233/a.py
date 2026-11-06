import sys

import numpy as np

input = sys.stdin.readline


MOD = 998244353


def query(m: int) -> bool:
    print(f"? {m}", flush=True)
    ans = input().strip()
    assert ans != "-1"
    return ans == "Yes"


def answer(m: int) -> None:
    print(f"! {m}", flush=True)


T = int(input())
for _ in range(T):
    N = int(input())

    a: list[int] = []
    if N % 2 == 0:
        if query(N // 2):
            a.append(N // 2)
        else:
            answer(2)
            continue

    yes_partner: list[int] = []
    no_partner: list[int] = []
    for m in range(1, (N - 1) // 2 + 1):
        if query(m):
            a.append(m)
            yes_partner.append(N - m)
        else:
            no_partner.append(N - m)

    if not yes_partner:
        a.extend(no_partner)
    elif not no_partner:
        # すでに a は確定している
        pass
    else:
        if len(yes_partner) < len(no_partner):
            is_s2 = False
            for m in yes_partner:
                if query(m):
                    is_s2 = True
                    answer(2)
                    break
            if is_s2:
                continue
            a.extend(no_partner)
        else:
            is_s2 = False
            for m in no_partner:
                if not query(m):
                    is_s2 = True
                    answer(2)
                    break
            if is_s2:
                continue
            a.extend(no_partner)

    b = [0] * N
    for x in a:
        b[x] = 1
    # 参考: https://maspypy.com/%E6%95%B0%E5%AD%A6%E3%83%BBnumpy-%E9%AB%98%E9%80%9F%E3%83%95%E3%83%BC%E3%83%AA%E3%82%A8%E5%A4%89%E6%8F%9Bfft%E3%81%AB%E3%82%88%E3%82%8B%E7%95%B3%E3%81%BF%E8%BE%BC%E3%81%BF
    size = 1 << (2 * N - 2).bit_length()
    f = np.fft.rfft(b, n=size)
    f *= f
    c = np.rint(np.fft.irfft(f, n=size)).astype(np.int64)

    for x in a:
        pairs = c[N - x] // 2
        if 1 <= N - 2 * x and N - 2 * x != x and b[N - 2 * x]:
            pairs -= 1
        if pairs > 0:
            answer(3)
            break
    else:
        answer(-1)
