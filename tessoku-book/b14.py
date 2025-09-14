N, K = map(int, input().split())
A = list(map(int, input().split()))

front = []
for i in range(1 << (N//2)):
    j = 0
    sum = 0
    while i > 0:
        if i & 1:
            sum += A[j]
        j += 1
        i >>= 1
    front.append(sum)

# print(front)

back = []
for i in range(1 << (N//2 + N % 2)):
    j = N//2
    sum = 0
    while i > 0:
        if i & 1:
            sum += A[j]
        j += 1
        i >>= 1
    back.append(sum)

# print(back)
back.sort()

for n in front:
    if n > K:
        continue

    target = K - n
    left, right = 0, len(back)-1
    while left <= right:
        mid = (left + right) // 2
        if back[mid] < target:
            left = mid + 1
        elif back[mid] > target:
            right = mid - 1
        else:
            print('Yes')
            exit()

print('No')
