N, S = map(int, input().split())
(*A,) = map(int, input().split())


def enumerate_half(elems: list[int]) -> dict[int, int]:
    dp = {0: 1}
    for a in elems:
        nxt = {}
        for s, cnt in dp.items():
            nxt[s] = nxt.get(s, 0) + cnt
            if s + a <= S:
                nxt[s + a] = nxt.get(s + a, 0) + cnt
        dp = nxt
    return dp


first_half = enumerate_half(A[: N // 2])
second_half = enumerate_half(A[N // 2 :])

ans = 0
for s, cnt in first_half.items():
    if S - s in second_half:
        ans += cnt * second_half[S - s]
print(ans)
