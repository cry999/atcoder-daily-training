N = int(input())

A = [list(map(int, input().split()))[1:] for _ in range(N)]
ans = [[] for _ in range(N)]

for i, a in enumerate(A):
    for j in a:  # j: 人 i がプレゼントを送った相手
        ans[j - 1].append(i + 1)

for a in ans:
    print(len(a), *a)
