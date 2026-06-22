N, K = map(int, input().split())
(*V,) = map(int, input().split())

# 途中で返すことはない。
# x 個とって、y 個返す。を全探索する？
# x + y <= K
# y <= x

ans = 0
for x in range(1, min(N, K) + 1):
    for y in range(x + 1):
        if x + y > K:
            break

        # 右から i こ、左から j ことって、最大 y このマイナスを返却する
        for i in range(x + 1):
            j = x - i
            s = 0
            minus = []
            for k in range(N):
                if k < i or N - j <= k:
                    s += V[k]
                    minus.append(V[k])
            minus.sort()
            s -= sum(minus[:y])
            ans = max(ans, s)
print(ans)
