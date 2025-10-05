N, K = map(int, input().split())
print('Yes' if K >= 2*(N-1) and K % 2 == 0 else 'No')
