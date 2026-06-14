N = int(input())

ranges = []

for _ in range(N):
    a, b = map(int, input().split())
    ranges.append((a, a + b - 1))

ranges.sort(reverse=True)

while ranges:
    l, r = ranges.pop()

# ranges = []
#
# for _ in range(N):
#     a, b = map(int, input().split())
#     ranges.append((a + b - 1, a))
#
# ranges.sort()
# # ログイン日が早い順に処理する。
#
# l0 = ranges[0][0]
# # sorted_ranges[i] := (r, l, d) := d 人がログインしている期間 (l, r)
# sorted_ranges = SortedList()
# for r, l in ranges:
#     i = sorted_ranges.bisect_left((l, 0, 0))
#
#     tmp = []
#     while i < len(sorted_ranges) and l <= sorted_ranges[i][0]:
#         r0, l0, d0 = sorted_ranges.pop(i)
#
#         if r < l0:  # 交差なし
#             tmp.append((r, l, 1))
#             tmp.append((r0, l0, d0))
#
#             break
#         elif l0 <= r <= r0:
#             if l < l0:
#                 tmp.append((l0 - 1, l, 1))
#             elif l0 < l:  # l0 < l <= r0
#                 tmp.append((l - 1, l0, d0))
#
#             tmp.append((r, max(l, l0), d0 + 1))
#
#             if r < r0:
#                 tmp.append((r0, r + 1, d0))
#
#             break
#         else:  # l <= r0 < r
#             if l < l0:
#                 tmp.append((l0 - 1, l, 1))
#             elif l0 < l:
#                 tmp.append((l - 1, l0, d0))
#
#             tmp.append((r0, max(l, l0), d0 + 1))
#             l = r0 + 1
#     else:
#         if l <= r:
#             tmp.append((r, l, 1))
#
#     for r, l, d in tmp:
#         sorted_ranges.add((r, l, d))
#     # print(f"[DEBUG] {sorted_ranges}")
#
# ans = [0] * N
# for r, l, d in sorted_ranges:
#     ans[d - 1] += (r - l) + 1
# print(*ans)
# # print(f"[DEBUG] {sorted_ranges}")
