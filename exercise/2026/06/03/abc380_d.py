S = input()
Q = int(input())
(*K,) = map(int, input().split())

N = len(S)

ans = []
for kq in K:
    kq -= 1
    # いくつめの文字列に存在するか
    n = kq // N
    # その中の何文字目に相当するか
    i = kq % N
    # n の bit 数が奇数なら T 偶数なら S に相当する。
    # print(f"{n.bit_count()=}: {n=:b} {i=}")
    if n.bit_count() % 2 == 0:
        ans.append(S[i])
    else:
        u, l = S[i].upper(), S[i].lower()
        ans.append(u if S[i].islower() else l)

print(*ans)
