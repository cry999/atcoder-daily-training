N = int(input())
print('\n'.join(
    f'{A} {B}' for A, B in sorted(
        tuple(map(int, input().split())) for _ in range(N)
    )))
