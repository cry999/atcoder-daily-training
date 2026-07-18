from math import prod

MOD = 998244353


N = int(input())
S = input().split()
L = [len(s) for s in S]

STATE = prod(L)


def encode(ks: list[int], lens: list[int]) -> int:
    state = 0
    for k, l in zip(ks, lens):
        state = state * l + k
    return state


def decode(state: int, lens: list[int]) -> list[int]:
    ks = []

    for l in reversed(lens):
        state, k = divmod(state, l)
        ks.append(k)

    return ks[::-1]


dp = {0: 1}
for _ in range(N):
    ndp = {}
    for state, value in dp.items():
        ks = decode(state, L)

        # 遷移を起こす文字の集合
        next_chars = {s[ks[i]] for i, s in enumerate(S)}

        for c in next_chars:
            nks = ks.copy()
            for i, s in enumerate(S):
                # 次に置く文字が遷移を起こす文字かどうかの判定
                if s[ks[i]] == c:
                    nks[i] += 1

            if any(nks[i] == len(s) for i, s in enumerate(S)):
                # 文字列全体を部分列に含む遷移があれば除外する。
                continue

            next_state = encode(nks, L)
            ndp[next_state] = (ndp.get(next_state, 0) + value) % MOD

        # next_chars に含まれない文字は遷移しない
        ndp[state] = (ndp.get(state, 0) + value * (26 - len(next_chars))) % MOD

    dp = ndp

print(sum(dp.values()) % MOD)
