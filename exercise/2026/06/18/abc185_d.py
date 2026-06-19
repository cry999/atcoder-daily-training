N, M = map(int, input().split())
(*A,) = map(int, input().split())
if len(A) == 0 or min(A) != 1:
    A.append(0)
if len(A) == 0 or max(A) != N:
    A.append(N + 1)
A.sort()

# stamp 幅
width = N
for i in range(len(A) - 1):
    if A[i + 1] - A[i] == 1:
        continue
    # 連続しているところはスタンプいらないので幅の候補から除外
    width = min(width, A[i + 1] - A[i] - 1)

ans = 0
for i in range(len(A) - 1):
    place = A[i + 1] - A[i] - 1
    if place == 0:
        continue
    ans += place // width + (place % width > 0)
print(ans)
