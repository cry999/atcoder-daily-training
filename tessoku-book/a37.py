N, M, B = map(int, input().split())
A = sum(map(int, input().split()))
C = sum(map(int, input().split()))
print(M*A + N*C + B*N*M)
