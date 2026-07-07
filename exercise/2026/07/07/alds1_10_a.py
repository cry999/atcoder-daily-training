N = int(input())
fib = [1] * (N + 1)

for n in range(2, N + 1):
    fib[n] = fib[n - 1] + fib[n - 2]
print(fib[N])
