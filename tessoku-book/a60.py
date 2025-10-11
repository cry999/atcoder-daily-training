# 株価をキーに日数の最大値を SegmentTree で管理する
# まずは株価がより高い最大日を求める。
# その後に、自分の日付を SegmentTree に突っ込む。

N = int(input())
A = list(map(int, input().split()))

stack = []
ans = []
for i, a in enumerate(A):
    while stack:
        d, v = stack.pop()
        if v <= a:
            continue
        ans.append(d)
        stack.append((d, v))
        stack.append((i+1, a))
        break
    else:
        ans.append(-1)
        stack.append((i+1, a))
print(*ans)
