# test4.py
# (基于参考代码2) 另一版本的标准回溯法，寻找空单元格列表

class SudokuSolverB:
    def __init__(self, board):
        self.board = board
        self.empty_cells = []
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    self.empty_cells.append((r, c))

    def is_valid(self, num, r, c):
        # 检查行
        if num in self.board[r]:
            return False
        # 检查列
        if num in [self.board[i][c] for i in range(9)]:
            return False
        # 检查3x3宫
        box_r_start, box_c_start = 3 * (r // 3), 3 * (c // 3)
        for i in range(box_r_start, box_r_start + 3):
            for j in range(box_c_start, box_c_start + 3):
                if self.board[i][j] == num:
                    return False
        return True

    def solve_recursive(self, k):
        if k == len(self.empty_cells):
            return True

        r, c = self.empty_cells[k]
        for num in range(1, 10):
            if self.is_valid(num, r, c):
                self.board[r][c] = num
                if self.solve_recursive(k + 1):
                    return True
                self.board[r][c] = 0
        return False

    def solve(self):
        if self.solve_recursive(0):
            return self.board
        return None

if __name__ == "__main__":
    puzzle = [[5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
              [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
              [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9]]
    solver = SudokuSolverB(puzzle)
    solution = solver.solve()
    for row in solution:
        print(row)