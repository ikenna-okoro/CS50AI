board = []
height = 8 
width = 8
# EMPTY = "EMPTY"
greet = "Hi"
neighbor = set()

for i in range(height):
    row = []
    for j in range(width):
        row.append(False)
    board.append(row)
for row in board:
    print(row)

i = int(input("Enter cell row: "))
j = int(input("Enter cell column: "))
if j > 8 or i > 8:
    raise Exception("Value out of range!")
cell = (i, j)
print(cell)

i, j = cell
if i in (0, height - 1) and j in (0, width - 1):
    print(cell)
else:
    print("not in set")

up = (i - 1), j
down = (i + 1), j
left = i, (j - 1)
right = i, (j + 1)
tp_left = (i - 1), (j - 1)
tp_right = (i - 1), (j + 1)
bt_left = (i + 1), (j - 1)
bt_right = (i + 1), (j + 1)

candidates = [up, down, left, right, tp_left, tp_right, bt_left, bt_right]
results = []

board[i][j] = "|-,-|"
for r, c in candidates:
    if 0 <= r < height and 0 <= c < width:
        results.append((r, c))
        board[r][c] = greet
print(results)
for row in board:
    print(row)


