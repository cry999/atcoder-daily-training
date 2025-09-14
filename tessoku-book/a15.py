N = int(input())
A = list(map(int, input().split()))
sorted_a = sorted(set(A))

B = [0] * N

for i in range(N):
    a = A[i]

    left, right = 0, len(sorted_a)-1
    while left <= right:
        mid = (left + right) // 2
        if sorted_a[mid] < a:
            left = mid + 1
        elif sorted_a[mid] >= a:
            right = mid - 1
    B[i] = left+1

print(*B)
