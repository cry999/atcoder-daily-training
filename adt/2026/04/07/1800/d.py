from collections import defaultdict

S = input()

freq = defaultdict(int)

max_char, max_freq = "", 0
for c in S:
    freq[c] += 1
    if freq[c] > max_freq:
        max_char, max_freq = c, freq[c]
    elif freq[c] == max_freq and c < max_char:
        max_char = c

print(max_char)
