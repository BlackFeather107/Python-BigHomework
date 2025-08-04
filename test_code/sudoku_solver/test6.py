# test6.py
# (整合1和2，但仅参考思路) 采用完全不同的实现，例如使用生成器(yield)

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None

def is_placement_valid(board, num, pos):
    r, c = pos
    # 检查行
    for i in range(9):
        if board[r][i] == num:
            return False
    # 检查列
    for i in range(9):
        if board[i][c] == num:
            return False
    # 检查宫
    box_r_start, box_c_start = 3 * (r // 3), 3 * (c // 3)
    for i in range(box_r_start, box_r_start + 3):
        for j in range(box_c_start, box_c_start + 3):
            if board[i][j] == num:
                return False
    return True

def solve_generator(board):
    find = find_empty(board)
    if not find:
        # yield board # 如果需要所有解，可以使用yield
        return True # 找到一个解即可
    else:
        r, c = find

    for num in range(1, 10):
        if is_placement_valid(board, num, (r, c)):
            board[r][c] = num

            if solve_generator(board):
                return True

            board[r][c] = 0
    return False

if __name__ == "__main__":
    puzzle = [[5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
              [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
              [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9]]
    solve_generator(puzzle)
    for row in puzzle:
        print(row)