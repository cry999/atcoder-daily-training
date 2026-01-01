N = int(input())
LR = [tuple(map(int, input().split())) for _ in range(N)]
sum_l = sum(l for l, _ in LR)
sum_r = sum(r for _, r in LR)

if not (sum_l <= 0 <= sum_r):
    print("No")
    exit()
# print(sum_l, sum_r)
print("Yes")
ans = []
for l, r in LR:
    if sum_l < 0:
        # print(f"  {0-sum_l=} vs {r-l=}")
        if 0 - sum_l < r - l:
            # 0-sum_l だけ寄せる。
            ans.append(l - sum_l)
            sum_l = 0
        else:
            # r に寄せる。
            ans.append(r)
            sum_l += r - l
    else:
        # sum_l は 0 になっている想定。
        # もう L から R に寄せる必要はない。
        ans.append(l)
print(*ans)
