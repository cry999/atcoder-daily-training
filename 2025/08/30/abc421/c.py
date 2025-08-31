N = int(input())
S = input()


print(min(map(lambda T: sum(abs(x - y) for x, y in zip(
    filter(lambda k: S[k] == 'A' and T[k] != S[k], range(N*2)),
    filter(lambda k: S[k] != 'A' and T[k] != S[k], range(N*2)),
)), (
    ''.join('A' if i % 2 == 0 else 'B' for i in range(2*N)),
    ''.join('B' if i % 2 == 0 else 'A' for i in range(2*N)),
))))
