N = int(input())
*A, = map(int, input().split())

max_even_1, max_even_2 = -1, -1
max_odd_1, max_odd_2 = -1, -1

for a in A:
    if a % 2:  # odd
        if max_odd_1 < a:
            max_odd_1, max_odd_2 = a, max_odd_1
        elif max_odd_2 < a:
            max_odd_2 = a
    else:  # even
        if max_even_1 < a:
            max_even_1, max_even_2 = a, max_even_1
        elif max_even_2 < a:
            max_even_2 = a

if max_even_2 == max_odd_2 == -1:
    print(-1)
elif max_even_2 == -1:
    print(max_odd_1+max_odd_2)
elif max_odd_2 == -1:
    print(max_even_1+max_even_2)
else:
    print(max(max_odd_1+max_odd_2, max_even_1+max_even_2))
