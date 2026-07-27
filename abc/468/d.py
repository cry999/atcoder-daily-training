S = input()
N = len(S)

ans = 0
for i in range(N):
    # 偶数文字数の回文
    j, k = i, i + 1
    c = 0
    while j >= 0 and k < N:
        c += S[j] != S[k]
        if c <= 1:
            # print(f"[DEBUG] {j=} - {k=}: ({c=})")
            ans += 1
        else:
            break
        j -= 1
        k += 1

    # 奇数文字数の回文
    j, k = i, i
    c = 0
    while j >= 0 and k < N:
        c += S[j] != S[k]
        if c <= 1:
            # print(f"[DEBUG] {j=} - {k=}: ({c=})")
            ans += 1
        else:
            break
        j -= 1
        k += 1

print(ans)
