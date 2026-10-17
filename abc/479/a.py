N = int(input())
(*A,) = map(int, input().split())
s = sum(a for i, a in enumerate(A) if i % 2 == 0)
print(s)
