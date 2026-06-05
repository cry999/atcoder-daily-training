N, S = map(int, input().split())
(*A,) = map(int, input().split())

sum_a = sum(A)

# n: 何周期分必要か
n = S // sum_a

if sum_a * n == S:
    # ちょうど n 周期分で S になるならそれが答え
    print("Yes")
else:
    # そうでないなら、 n 周期分の後に、 A のどこかまで足せば S になるか
    # 調べる。
    s = S - sum_a * n

    c = A[0]
    l, r = 0, 0
    while l < N:
        r = max(r, l)
        while r < 2 * N and c < s:
            r += 1
            c += A[r % N]

        # print(f"{l=}, {r=}, {c=}, {s=}")
        if c == s:
            break

        c -= A[l]
        l += 1

    if c == s:
        print("Yes")
    else:
        print("No")
        # print("No", c, s)
