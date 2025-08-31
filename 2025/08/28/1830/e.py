N = int(input())
# スタート
A = list(sorted(map(int, input().split())))

S = sum(A)
# ゴール
B = [S // N + (1 if (N-i-1) < S % N else 0) for i in range(N)]

# sum(A[k]-B[k]) を 0 にするのが目的
# 操作1回で 2 減らせるので、sum(A[k]-B[k])//2 が答え

print(sum(abs(a - b) for a, b in zip(A, B)) // 2)
