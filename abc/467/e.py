from collections import defaultdict

N, M = map(int, input().split())
# A = list(range(10))
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

# operaiton: A[0] に何も足さない場合の操作回数
operation = 0
# delta: A[0] の操作回数を 1 増やした時の (剰余による変動を無視した) 操作回数の変化
delta = 1
# events[k] = v:
#   k := delta に含まれない遷移 (剰余による大きな変動) が起きる A[0] の操作回数
#   v := k -> k+1 に A[0] の操作回数が遷移する時の変化量
events = defaultdict(int)

prev_d = 0
for i in range(N - 1):
    d = (B[i] - A[i + 1] - A[i] - prev_d) % M

    operation += d
    if (i + 1) % 2 == 0:
        # A[0] が含まれる側は d+k = M-1 (mod M) となる時に
        # さらにもう一回遷移すると、寄与分が M = 0 (mod M) となる。
        # なので、この回を記録するとともに、この回では変化量への寄与 -M
        # (本来 M になるはずが 0 になるので) を記録する。
        events[M - 1 - d] -= M
        # A[0] が含まれる側は 1 要素につき +1 することになる
        # (剰余による変動を無視した場合) ので、delta にそれを記録する。
        delta += 1
    else:
        # (d - k) % M は k=d のとき 0。
        # その次の k=d -> d+1 の遷移で 0 -> M-1 と折り返すため、
        # 通常の -1 に対して追加で +M の補正が入る。
        events[d] += M
        delta -= 1

    prev_d = d

assert delta == N % 2

cur_k = 0
ans = operation
for k in sorted(events):
    if k >= M - 1:
        break

    # cur_k -> k 回目の遷移 (大変動含まず)
    operation += delta * (k - cur_k)
    cur_k = k

    # 今回は delta = 0 or 1 なのでここで ans が最小値をとることはない。
    # よって以下の操作は不要。
    # ans = min(ans, operation)

    # k -> k+1 回目の遷移 (大変動)
    operation += delta + events[k]
    cur_k += 1

    ans = min(ans, operation)
print(ans)
