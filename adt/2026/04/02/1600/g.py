N, M = map(int, input().split())
(*X,) = map(int, input().split())

# cum[x]: x から x+1 への端を渡れなくした時の移動コストを累積和で計算する。
cum = [0] * N

for i in range(M - 1):
    src = X[i] - 1
    dst = X[i + 1] - 1

    # print(f"{src=} -> {dst=}")

    if src > dst:
        # 移動の向きは計算に関係ないので、処理しやすいように src < dst に揃える
        src, dst = dst, src

    # src と dst の間の橋を通れなくした場合は src -> 1 -> N -> dst と移動するので
    # そのコストを加える。
    cost = src + (N - dst)
    cum[src] += cost
    cum[dst] -= cost
    # print(f"  1: {cost=}")
    # print(f"  1: {cum=}")

    # dst 以降、src 以前の端を通れなくした場合は、src -> dst と移動するのでその
    # コストを加える。
    cost = dst - src
    cum[dst] += cost
    cum[0] += cost
    cum[src] -= cost

    # print(f"  2: {cost=}")
    # print(f"  2: {cum=}")

for i in range(1, N):
    cum[i] += cum[i - 1]

# print(*cum)
print(min(cum))
