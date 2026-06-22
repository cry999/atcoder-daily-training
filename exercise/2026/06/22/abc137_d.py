from sortedcontainers import SortedList
import sys

input = sys.stdin.readline

N, M = map(int, input().split())

# M-1 日目から逆に見ていって、現在受けても報酬が間に合わないバイトの報酬がもらえるまでの日数が短い順
non_targets = SortedList()
# M-1 日目から逆に見ていって、現在受けて報酬が間に合うバイトの報酬が大きい順
targets = SortedList()

for _ in range(N):
    days, reward = map(int, input().split())
    non_targets.add((days, reward))

total_reward = 0
for remain in range(1, M + 1):
    # 残り日数が remain しかないなら、remain 以下で受けられるバイトで最大報酬
    # を受けた方がいい
    while non_targets and non_targets[0][0] <= remain:
        _, reward = non_targets.pop(0)
        targets.add(reward)

    if targets:
        total_reward += targets.pop()

print(total_reward)
