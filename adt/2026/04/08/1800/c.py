A, B = map(int, input().split())

while A and B:
    a = A % 10
    b = B % 10
    if a + b > 9:
        print("Hard")
        break
    A //= 10
    B //= 10
else:
    print("Easy")
