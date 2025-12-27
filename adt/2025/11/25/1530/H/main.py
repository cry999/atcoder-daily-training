import heapq


MOD = 998244353

N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]

# 各ダイスの最大の面ごとに処理するので、各ダイスの処理していない
# 面の数を覚えておくことで、remain_total - remain_rows[i] が
# i 番目のダイスが最大の面になる場合の数になる。
remain_total = pow(6, N, MOD)
remain_rows = [6]*N

queue = []
for i, a in enumerate(A):
    for n in a:
        heapq.heappush(queue, (-n, i))

ans = 0
while queue:
    n, i = heapq.heappop(queue)
    a = remain_total * pow(remain_rows[i], MOD-2, MOD)
    ans += -n * a
    ans %= MOD
    remain_total += MOD-a
    remain_total %= MOD
    remain_rows[i] -= 1
    # いずれかの行が全て処理されたら終了。
    if remain_rows[i] == 0:
        break

denom = pow(6, MOD-2, MOD)
denom = pow(denom, N, MOD)
ans *= denom
ans %= MOD
print(ans)
