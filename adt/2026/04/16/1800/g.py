N, L, R = map(int, input().split())
(*A,) = map(int, input().split())

# dp_right[i] := i .. N まで操作が完了した時の i .. N の総和の最小値
dp_right = [float("inf")] * (N + 1)
dp_right[N] = 0

for i in range(N, 0, -1):
    dp_right[i - 1] = min(dp_right[i] + A[i - 1], R * (N - i + 1))


# dp_left[i] := 0 .. i まで操作が完了した時の 0..i の総和の最小値
dp_left = [float("inf")] * (N + 1)
dp_left[0] = 0

for i in range(N):
    dp_left[i + 1] = min(dp_left[i] + A[i], L * (i + 1))

print(min(r + l for r, l in zip(dp_right, dp_left)))
