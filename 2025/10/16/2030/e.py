N = int(input())

A = 1
count = 0
while A*A*A <= N:
    B = A
    while A*B*B <= N:
        count += (N//(A*B))-B+1
        B += 1
    A += 1

print(count)
