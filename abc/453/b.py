T, X = map(int, input().split())
saved, *A = map(int, input().split())

print(0, saved)
for t in range(T):
    if abs(A[t] - saved) >= X:
        saved = A[t]
        print(t + 1, saved)
