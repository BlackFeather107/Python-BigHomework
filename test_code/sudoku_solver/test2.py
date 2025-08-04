# test2.py
# (大幅抄袭test1) 替换了类、方法和变量的命名

class PuzzleHandler:
    def __init__(self, grid):
        self.grid = grid
        self.row_tracker = [set() for _ in range(9)]
        self.col_tracker = [set() for _ in range(9)]
        self.box_tracker = [set() for _ in range(9)]
        
        for row_idx in range(9):
            for col_idx in range(9):
                if self.grid[row_idx][col_idx] != 0:
                    val = self.grid[row_idx][col_idx]
                    box_id = (row_idx // 3) * 3 + col_idx // 3
                    self.row_tracker[row_idx].add(val)
                    self.col_tracker[col_idx].add(val)
                    self.box_tracker[box_id].add(val)

    def check_placement(self, val, row_idx, col_idx):
        box_id = (row_idx // 3) * 3 + col_idx // 3
        return val not in self.row_tracker[row_idx] and val not in self.col_tracker[col_idx] and val not in self.box_tracker[box_id]

    def search(self, row_idx, col_idx):
        if row_idx == 9:
            return True

        next_row, next_col = (row_idx, col_idx + 1) if col_idx < 8 else (row_idx + 1, 0)

        if self.grid[row_idx][col_idx] != 0:
            return self.search(next_row, next_col)

        for val in range(1, 10):
            if self.check_placement(val, row_idx, col_idx):
                self.grid[row_idx][col_idx] = val
                box_id = (row_idx // 3) * 3 + col_idx // 3
                self.row_tracker[row_idx].add(val)
                self.col_tracker[col_idx].add(val)
                self.box_tracker[box_id].add(val)

                if self.search(next_row, next_col):
                    return True

                self.grid[row_idx][col_idx] = 0
                self.row_tracker[row_idx].remove(val)
                self.col_tracker[col_idx].remove(val)
                self.box_tracker[box_id].remove(val)
        
        return False

    def run(self):
        if self.search(0, 0):
            return self.grid
        return None

if __name__ == "__main__":
    problem = [[5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
               [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
               [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9]]
    handler = PuzzleHandler(problem)
    answer = handler.run()
    for r in answer:
        print(r)