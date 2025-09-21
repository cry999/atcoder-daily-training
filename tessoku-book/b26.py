N = int(input())

if N < 2:
    exit()

print(2)

for i in range(3, N+1, 2):
    j = 3
    while j * j <= i:
        if i % j == 0:
            break
        j += 2
    else:
        print(i)
