from bisect import bisect_left

A, B, C, D = map(int, input().split())


def eratosthenes(n: int):
    is_not_prime = [0] * (n + 1)
    primes = []

    for p in range(2, n + 1):
        if is_not_prime[p]:
            continue
        primes.append(p)
        for k in range(p + p, n + 1, p):
            is_not_prime[k] += 1

    return primes, is_not_prime


primes, _ = eratosthenes(200)


def solve():
    for n1 in range(A, B + 1):
        for n2 in range(C, D + 1):
            i = bisect_left(primes, n1 + n2)
            if i < len(primes) and primes[i] == n1 + n2:
                # found -> aoki wins
                # print(f"[DEBUG] {n1=}, {n2=}, {n1+n2=}, {primes[i]=}")
                break
            # not found takahashi wins
            continue
        else:
            # break していない -> aoki が素数にできなくて負け
            return True
    return False


print("Takahashi" if solve() else "Aoki")
