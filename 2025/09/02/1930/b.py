N, S = int(input()), input()
print('Yes' if S in (
    ''.join('M' if i % 2 else 'F' for i in range(N)),
    ''.join('F' if i % 2 else 'M' for i in range(N)),
) else 'No')
