X = input()
normal = 'abcdefghijklmnopqrstuvwxyz'
d = {X[i]: normal[i] for i in range(len(X))}


N = int(input())
print('\n'.join(sorted([input() for _ in range(N)],
      key=lambda s: ''.join(d[c] for c in s))))
