A, B = map(int, input().split())

if A + B == 9 or A * B == 9 or A - B == 9 or (A % B == 0 and A // B == 9):
    print("Nine")
else:
    print("Nein")
