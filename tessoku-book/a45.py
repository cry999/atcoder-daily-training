N, C = input().split()
N = int(N)
A = input()

# W = 0 なら、最初と最後のスコアが mod 3 で等しい
# W = 1 なら、(最初のスコア) - (N-1) と最後のスコアが mod 3 で等しい
# W = 2 なら、(最初のスコア) + (N-1) と最後のスコアが mod 3 で等しい
W = 2
B = (W + 1) % 3
R = (B + 1) % 3

start_score = sum(W if c == 'W' else B if c == 'B' else R for c in A) % 3
target_score = W if C == 'W' else B if C == 'B' else R
if W == 0:
    print('Yes' if start_score == target_score else 'No')
elif W == 1:
    print('Yes' if (start_score - (N-1) - target_score) % 3 == 0 else 'No')
else:  # W == 2
    print('Yes' if (start_score + (N-1) - target_score) % 3 == 0 else 'No')
