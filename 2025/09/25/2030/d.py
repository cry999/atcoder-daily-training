import math


A, B = map(int, input().split())

C = math.sqrt(A*A + B*B)
print(A / C, B / C)
