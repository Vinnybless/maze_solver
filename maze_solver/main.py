import time
import random
from tkinter import Tk, BOTH, Canvas


class Window:
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("Maze Solver")
        self.__canvas = Canvas(self.__root, bg="white", height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line, fill_color="black"):
        line.draw(self.__canvas, fill_color)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def draw(self, canvas, fill_color="black"):
        canvas.create_line(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=fill_color, width=2
        )


class Cell:
    def __init__(self, win=None):
        self._x1 = None
        self._x2 = None
        self._y1 = None
        self._y2 = None
        self._win = win
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.visited = False

    def draw(self, x1, y1, x2, y2):
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        if self.has_top_wall:
            line = Line(Point(x1, y1), Point(x2, y1))
            self._win.draw_line(line)
        else:
            line = Line(Point(x1, y1), Point(x2, y1))
            self._win.draw_line(line, "white")
        if self.has_right_wall:
            line = Line(Point(x2, y1), Point(x2, y2))
            self._win.draw_line(line)
        else:
            line = Line(Point(x2, y1), Point(x2, y2))
            self._win.draw_line(line, "white")
        if self.has_bottom_wall:
            line = Line(Point(x1, y2), Point(x2, y2))
            self._win.draw_line(line)
        else:
            line = Line(Point(x1, y2), Point(x2, y2))
            self._win.draw_line(line, "white")
        if self.has_left_wall:
            line = Line(Point(x1, y1), Point(x1, y2))
            self._win.draw_line(line)
        else:
            line = Line(Point(x1, y1), Point(x1, y2))
            self._win.draw_line(line, "white")

    def get_center(self):
        xmid = (self._x1 + self._x2) / 2
        ymid = (self._y1 + self._y2) / 2
        return Point(abs(xmid), abs(ymid))

    def draw_move(self, to_cell, undo=False):
        line_color = "red"
        if undo:
            line_color = "grey"
        p1 = self.get_center()
        p2 = to_cell.get_center()
        self._win.draw_line(Line(p1, p2), line_color)


class Maze:
    def __init__(
            self,
            x1,
            y1,
            num_rows,
            num_cols,
            cell_size_x,
            cell_size_y,
            seed=None,
            win=None
    ):
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        self.seed = seed
        self._cells = []
        self._create_cells()
        self._break_entrance_and_exit()
        if self.seed is not None:
            random.seed(self.seed)
        self._break_walls_r(0, 0)
        self._reset_cells_visited()

    def _create_cells(self):
        for i in range(self.num_rows):
            row = []
            for j in range(self.num_cols):
                row.append(Cell(self.win))
            self._cells.append(row)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self._draw_cell(i, j)

    def _draw_cell(self, i, j):
        if self.win is None:
            return
        cell = self._cells[i][j]
        x = self.x1 + j * self.cell_size_x
        y = self.y1 + i * self.cell_size_y
        x2 = x + self.cell_size_x
        y2 = y + self.cell_size_y
        cell.draw(x, y, x2, y2)
        self._animate()

    def _animate(self):
        if self.win is None:
            return
        self.win.redraw()
        time.sleep(0.002)

    def _break_entrance_and_exit(self):
        c1 = self._cells[0][0].has_left_wall = False
        self._draw_cell(0, 0)
        c2 = self._cells[self.num_rows - 1][self.num_cols - 1].has_right_wall = False
        self._draw_cell(self.num_rows - 1, self.num_cols - 1)

    def _break_walls_r(self, i, j):
        self._cells[i][j].visited = True
        while True:
            to_visit = []
            if i > 0 and not self._cells[i - 1][j].visited:
                to_visit.append((i - 1, j))
            if i < self.num_rows - 1 and not self._cells[i + 1][j].visited:
                to_visit.append((i + 1, j))
            if j > 0 and not self._cells[i][j - 1].visited:
                to_visit.append((i, j - 1))
            if j < self.num_cols - 1 and not self._cells[i][j + 1].visited:
                to_visit.append((i, j + 1))

            if len(to_visit) == 0:
                self._draw_cell(i, j)
                return
            else:
                rand_direction = random.choice(to_visit)
                if rand_direction == (i - 1, j):
                    self._cells[i][j].has_top_wall = False
                    self._cells[rand_direction[0]][rand_direction[1]].has_bottom_wall = False
                elif rand_direction == (i + 1, j):
                    self._cells[i][j].has_bottom_wall = False
                    self._cells[rand_direction[0]][rand_direction[1]].has_top_wall = False
                elif rand_direction == (i, j - 1):
                    self._cells[i][j].has_left_wall = False
                    self._cells[rand_direction[0]][rand_direction[1]].has_right_wall = False
                elif rand_direction == (i, j + 1):
                    self._cells[i][j].has_right_wall = False
                    self._cells[rand_direction[0]][rand_direction[1]].has_left_wall = False

                self._break_walls_r(rand_direction[0], rand_direction[1])

    def _reset_cells_visited(self):
        for i in self._cells:
            for j in i:
                j.visited = False

    def solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        self._animate()
        self._cells[i][j].visited = True

        if (i == self.num_rows - 1) and (j == self.num_cols - 1):
            return True

        up = None
        down = None
        left = None
        right = None

        if i > 0:
            up = self._cells[i-1][j]
        if i < self.num_rows - 1:
            down = self._cells[i+1][j]
        if j > 0:
            left = self._cells[i][j-1]
        if j < self.num_cols - 1:
            right = self._cells[i][j+1]

        if up and not up.has_bottom_wall and not up.visited:
            self._cells[i][j].draw_move(up)
            if self._solve_r(i-1, j):
                return True
            else:
                self._cells[i][j].draw_move(up, undo=True)
        if down and not down.has_top_wall and not down.visited:
            self._cells[i][j].draw_move(down)
            if self._solve_r(i+1, j):
                return True
            else:
                self._cells[i][j].draw_move(down, undo=True)
        if left and not left.has_right_wall and not left.visited:
            self._cells[i][j].draw_move(left)
            if self._solve_r(i, j-1):
                return True
            else:
                self._cells[i][j].draw_move(left, undo=True)
        if right and not right.has_left_wall and not right.visited:
            self._cells[i][j].draw_move(right)
            if self._solve_r(i, j+1):
                return True
            else:
                self._cells[i][j].draw_move(right, undo=True)
        return False


def main():
    win = Window(800, 600)
    m = Maze(4, 4, 40, 40, 20, 20, None, win)
    m.solve()
    win.wait_for_close()


if __name__ == "__main__":
    main()
