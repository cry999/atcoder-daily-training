N = int(input())
(*A,) = map(int, input().split())

# 渡せない人
offset = [0] * (N + 1)

for i in range(N):
    older = i - offset[i]
    younger = N - i - 1

    A[i] += older - younger

    if A[i] < 0:
        # 若い方から A[i] 人には渡せない
        offset[A[i] - 1] += 1
        A[i] = 0

    offset[i + 1] += offset[i]

print(*A)
