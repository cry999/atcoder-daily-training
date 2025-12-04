import math

W, B = map(int, input().split())
W *= 1000

n = math.ceil((W+1)/B)
print(n)
