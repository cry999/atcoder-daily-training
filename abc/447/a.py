from math import ceil

N, M = map(int, input().split())
if M <= ceil(N / 2):
    print("Yes")
else:
    print("No")
