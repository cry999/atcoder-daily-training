T = int(input())

for _ in range(T):
    N = int(input())
    S = input()

    if N == 1:
        print(S)
        continue
    elif N == 2:
        print(min(S, S[1] + S[0]))
        continue

    # 一番最初に順番が逆転しているところを l として良い。
    # r にするのは、S[l] 以下で最小の位置

    # 逆転しているところがなければ、末尾の2文字を交換する

    l = -1
    for i in range(N - 1):
        if S[i] > S[i + 1]:
            l = i
            break

    ans = ""
    if l >= 0:
        ans = S[:l]

    r = N
    for i in range(l, N - 1):
        if S[i + 1] > S[l]:
            r = i + 1
            break

    ans += S[l + 1 : r]
    if l >= 0:
        ans += S[l]
    ans += S[r:]

    # print(l, r, ans)
    print(ans)
