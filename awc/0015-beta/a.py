(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

print(sum(a * b for a, b in zip(A, B)))
