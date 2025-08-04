# test5.py
# (整合1和2，抄袭成分重) 采用test4的“寻找空单元格”思路，但内部实现大量复用test1的逻辑

class HybridSolver:
    def __init__(self, board):
        self.board = board
        # 混合点1: 复用test1的 trackers
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
        
        # 混合点2: 采用test4的 empty_cells 列表
        self.empty_cells = []
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    self.empty_cells.append((r, c))

    def is_valid(self, num, r, c):
        # 混合点3: 复用test1的高效is_valid
        box_index = (r // 3) * 3 + c // 3
        return num not in self.rows[r] and num not in self.cols[c] and num not in self.boxes[box_index]

    def backtrack(self, k):
        # 混合点4: 采用test4的递归结构
        if k == len(self.empty_cells):
            return True

        r, c = self.empty_cells[k]
        for num in range(1, 10):
            if self.is_valid(num, r, c):
                self.board[r][c] = num
                box_index = (r // 3) * 3 + c // 3
                self.rows[r].add(num)
                self.cols[c].add(num)
                self.boxes[box_index].add(num)

                if self.backtrack(k + 1):
                    return True

                self.board[r][c] = 0
                self.rows[r].remove(num)
                self.cols[c].remove(num)
                self.boxes[box_index].remove(num)
        return False

    def solve(self):
        if self.backtrack(0):
            return self.board
        return None

if __name__ == "__main__":
    puzzle = [[5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
              [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
              [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9]]
    solver = HybridSolver(puzzle)
    solution = solver.solve()
    for row in solution:
        print(row)