from sortedcontainers import SortedDict

N = int(input())
S = input()
(*W,) = map(int, input().split())

sd = SortedDict()

for s, w in zip(S, W):
    if w not in sd:
        sd[w] = [0, 0]
    sd[w][int(s)] += 1

f = S.count("1")
ans = f
for w, (cnt0, cnt1) in sd.items():
    f += cnt0 - cnt1
    ans = max(ans, f)
print(ans)
