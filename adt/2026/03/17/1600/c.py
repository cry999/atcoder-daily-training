N, K = map(int, input().split())
(*A,) = map(int, input().split())

cnt = 0
i = 0
while i < N:
    ride_on = 0
    while i < N and ride_on + A[i] <= K:
        ride_on += A[i]
        i += 1
    cnt += 1

print(cnt)
