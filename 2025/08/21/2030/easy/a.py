N, M = map(int, input().split())

A = list(map(int, input().split()))
B = list(map(int, input().split()))

score = 0
for question in B:
    score += A[question - 1]

print(score)
