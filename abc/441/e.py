N = int(input())
S = input()

cum_a = [0] * (N + 1)
cum_b = [0] * (N + 1)

for i in range(N):
    cum_a[i + 1] = cum_a[i] + (S[i] == "A")
    cum_b[i + 1] = cum_b[i] + (S[i] == "B")
cum_c = [a - b for a, b in zip(cum_a, cum_b)]

hist = {}
for v in cum_c:
    hist[v] = hist.get(v, 0) + 1

diff = 0
for k, v in hist.items():
    if k > 0:
        diff += v

ans = 0
for i in range(N):
    ans += diff
    # print(i, cum_c[i], diff, hist)
    if cum_c[i + 1] == cum_c[i]:
        hist[cum_c[i]] -= 1
    elif cum_c[i + 1] > cum_c[i]:
        diff -= hist[cum_c[i + 1]]
        hist[cum_c[i]] -= 1
    else:
        hist[cum_c[i]] -= 1
        diff += hist[cum_c[i]]
print(ans)
