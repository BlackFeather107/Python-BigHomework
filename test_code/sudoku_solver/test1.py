# test1.py
# (基于参考代码1) 标准的回溯法实现

class SudokuSolver:
    def __init__(self, board):
        self.board = board
        self.rows = [set() for _ in range(9)]
        self.cols = [set() for _ in range(9)]
        self.boxes = [set() for _ in range(9)]
        
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != 0:
                    num = self.board[r][c]
                    box_index = (r // 3) * 3 + c // 3
                    self.rows[r].add(num)
                    self.cols[c].add(num)
                    self.boxes[box_index].add(num)

    def is_valid(self, num, r, c):
        box_index = (r // 3) * 3 + c // 3
        return num not in self.rows[r] and num not in self.cols[c] and num not in self.boxes[box_index]

    def backtrack(self, r, c):
        if r == 9:
            return True # 找到解

        next_r, next_c = (r, c + 1) if c < 8 else (r + 1, 0)

        if self.board[r][c] != 0:
            return self.backtrack(next_r, next_c)

        for num in range(1, 10):
            if self.is_valid(num, r, c):
                self.board[r][c] = num
                box_index = (r // 3) * 3 + c // 3
                self.rows[r].add(num)
                self.cols[c].add(num)
                self.boxes[box_index].add(num)

                if self.backtrack(next_r, next_c):
                    return True

                self.board[r][c] = 0
                self.rows[r].remove(num)
                self.cols[c].remove(num)
                self.boxes[box_index].remove(num)
        
        return False

    def solve(self):
        if self.backtrack(0, 0):
            return self.board
        return None

if __name__ == "__main__":
    puzzle = [[5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
              [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
              [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9]]
    solver = SudokuSolver(puzzle)
    solution = solver.solve()
    for row in solution:
        print(row)