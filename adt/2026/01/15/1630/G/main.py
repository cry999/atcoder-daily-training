S = input()
K = int(input())
N = len(S)

num_dots = [0] * (N + 1)
for i in range(N):
    num_dots[i + 1] = num_dots[i]
    if S[i] == ".":
        num_dots[i + 1] += 1

# 二分探索による解法 O(N log N)
# 一応 TLE はしない。
#
# lo, hi = 0, N + 1
#
# while hi - lo > 1:
#     mi = (lo + hi) // 2
#     # print(f"{lo=}, {hi=}")
#
#     i = 0
#     while i + mi <= N:
#         # print(mi, i, num_dots[i + mi], num_dots[i])
#         if num_dots[i + mi] - num_dots[i] <= K:
#             # print("break")
#             break
#         i += 1
#     else:
#         hi = mi
#         continue
#     lo = mi
#
# print(lo)

# (l, r] の '.' の数が K 以下であるような r-l の最大値を尺取法で求める。
# O(N)
l, r = 0, 0
ans = r - l
while l <= N:
    if r < l:
        r = l

    while r + 1 <= N and num_dots[r + 1] - num_dots[l] <= K:
        r += 1
    ans = max(ans, r - l)
    l += 1
print(ans)
