N = int(input())
s = input()

num_a = 0
move_to_odd = 0
move_to_even = 0
for i, c in enumerate(s):
    if c == 'A':
        move_to_odd += abs(2*num_a - i)
        move_to_even += abs(2*num_a+1 - i)
        num_a += 1

print(min(move_to_odd, move_to_even))
