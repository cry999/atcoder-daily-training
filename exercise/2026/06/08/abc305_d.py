from bisect import bisect_right
from bisect import bisect_left

N = int(input())
(*A,) = map(int, input().split())

sleep = [A[2 * i + 1] for i in range(N // 2)]
awake = [A[2 * (i + 1)] for i in range(N // 2)]

total = [0] * (N // 2 + 1)

for i in range(N // 2):
    total[i + 1] = total[i] + (awake[i] - sleep[i])

# print(f"[DEBUG] {total=}")
# print(f"[DEBUG] {awake=}")
# print(f"[DEBUG] {sleep=}")

Q = int(input())
for _ in range(Q):
    l, r = map(int, input().split())

    i = bisect_left(awake, l)
    j = bisect_right(sleep, r)

    if i == len(awake) or j == 0:
        # 指定された時間に寝ていない。
        print(0)
        continue

    ans = total[j] - total[i]
    # print(f"[DEBUG] {ans=}")
    if sleep[i] <= l <= awake[i]:
        # 寝ている最中に l がある。
        ans -= l - sleep[i]

    if sleep[j - 1] <= r <= awake[j - 1]:
        ans -= awake[j - 1] - r

    # print(f"[DEBUG] {i=}, {j=}, {l=}, {r=}")
    print(ans)
