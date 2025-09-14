import bisect


N = int(input())

numbers = [i + 1 for i in range(2*N+1)]

while True:
    my_number = numbers.pop(0)
    print(my_number)

    aoki_number = int(input())
    if aoki_number == 0:
        break
    else:
        numbers.pop(bisect.bisect_left(numbers, aoki_number))
