N = int(input())
ctz = 0
while N % 2 == 0:
    ctz += 1
    N >>= 1
print(ctz)
