Q = int(input())

for _ in range(Q):
    a, b = map(int, input().split())
    # 大小は関係ないので、a <= b と仮定する。
    if a > b:
        a, b = b, a

    ans = 0
    prev = 0
    for i in range(1, b):
        j = (a * b - 1) // i
        if j != prev and i * j < a * b:
            print(f"[DEBUG] {i=}, {j=}")
            if j != a:
                ans += 1
                prev = j
    print(ans)
