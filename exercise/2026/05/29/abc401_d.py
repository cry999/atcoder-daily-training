N, K = map(int, input().split())
S = input()

T = []
o_pos = 0  # o をおける位置の数
prev_o = False  # o をおける位置で o を仮置きしたかどうか
for i, s in enumerate(S):
    if s == "o" or s == ".":
        T.append(s)
        K -= s == "o"
        prev_o = s == "o"
    else:  # "?"
        if i > 0 and S[i - 1] == "o":
            T.append(".")
            prev_o = False
        elif i + 1 < N and S[i + 1] == "o":
            T.append(".")
            prev_o = False
        else:
            if not prev_o:
                o_pos += 1
                prev_o = True
            else:
                prev_o = False
            T.append("?")

if K == 0:
    T = [t if t != "?" else "." for t in T]

if o_pos == K:
    # o をおける位置の数がちょうど K なら置き方が置き方が確定している箇所がある可能性がある。

    # tmp1 は左から詰めて置いてみる。tmp2 は右から詰めておいてみる
    # どちらも同じ場所においているものは確定とみなして良い。
    tmp1 = T[:]
    tmp2 = T[:]

    for i in range(N):
        if tmp1[i] != "?":
            continue

        if i > 0 and tmp1[i - 1] == "o":
            tmp1[i] = "."
        elif i + 1 < N and tmp1[i + 1] == "o":
            tmp1[i] = "."
        else:
            tmp1[i] = "o"

    for i in range(N - 1, -1, -1):
        if tmp2[i] != "?":
            continue

        if i > 0 and tmp2[i - 1] == "o":
            tmp2[i] = "."
        elif i + 1 < N and tmp2[i + 1] == "o":
            tmp2[i] = "."
        else:
            tmp2[i] = "o"

    for i in range(N):
        if tmp1[i] == tmp2[i]:
            T[i] = tmp1[i]

print("".join(T))
