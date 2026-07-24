T = int(input())
for _ in range(T):
    K = int(input())

    k = K
    while True:
        if "00" in str(k):
            print(k)
            break
        k += K
