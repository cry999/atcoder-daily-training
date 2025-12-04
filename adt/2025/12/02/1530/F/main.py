N = int(input())

S = [input() for _ in range(N)]

# m[n][p] = 数字 n が p 桁目に登場する個数
m = {n: {} for n in range(10)}
for s in S:
    for i, c in enumerate(s):
        m[int(c)][i] = m[int(c)].get(i, 0)+1

# O(n * p * N) = O(10**5)
min_time = (N-1)*10 + 1
for n in range(10):
    max_freq = max(m[n].values())
    time = max(filter(lambda x: x[1] == max_freq, m[n].items()))[0] \
        + (max(m[n].values())-1)*10
    min_time = min(min_time, time)
print(min_time)
