# >>> atcoder-stat >>>
# started_at  = 2026-11-24T07:17:59+09:00
# solved_at   = 2026-11-24T07:59:15+09:00
# duration_ms = 2476897
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
S = input()
T = [""] * N
for i in range(N):
    if S[i] != "?":
        T[i] = S[i]
    elif i > 0 and S[i - 1] == "o" or i + 1 < N and S[i + 1] == "o":
        T[i] = "."
    else:
        T[i] = "?"

need_o = K - T.count("o")
can_place_o = 0
i = 0
while i < N:
    if T[i] != "?":
        i += 1
        continue

    j = 0
    while i + j < N and T[i + j] == "?":
        j += 1
    can_place_o += (j + 1) // 2
    i += j

print(f"[DEBUG] {need_o=} {can_place_o=}")
if need_o == can_place_o:
    # おける箇所がギリギリの場合は、? の連続数が奇数の箇所は置き方一意
    i = 0
    while i < N:
        if T[i] != "?":
            i += 1
            continue
        j = 0
        while i + j < N and T[i + j] == "?":
            j += 1
        if j % 2 == 1:
            for k in range(j):
                T[i + k] = "o" if k % 2 == 0 else "."
        i += j
elif need_o == 0:
    for i in range(N):
        if T[i] == "?":
            T[i] = "."


print("".join(T))
