N = int(input())
*A, = map(int, input().split())

hist = {}

for a in A:
    hist[a] = hist.get(a, 0) + 1

# v >= 2 以上を足したいが、結果的に v=0, 1 の時は値が 0 になるので、そのまま計算して良い
print(sum((N-v)*v*(v-1)//2 for k, v in hist.items()))
