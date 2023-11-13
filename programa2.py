import tkinter as tk
from tkinter import messagebox
import random


def iniciarPartida():
    class Buscaminas:
        def __init__(self, master):
            self.master = master
            self.master.title("Buscaminas")

            self.rows = 6
            self.cols = 7
            self.mines = 15
            self.board = [[0] * self.cols for _ in range(self.rows)]
            self.flags = [[False] * self.cols for _ in range(self.rows)]
            self.generate_mines()
            self.calculate_numbers()

            self.buttons = [[None] * self.cols for _ in range(self.rows)]
            self.create_widgets()

        def generate_mines(self):
            mines_generated = 0
            while mines_generated < self.mines:
                row = random.randint(0, self.rows - 1)
                col = random.randint(0, self.cols - 1)
                if self.board[row][col] != "M":
                    self.board[row][col] = "M"
                    mines_generated += 1

        def calculate_numbers(self):
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] != "M":
                        count = 0
                        for x in range(max(0, i - 1), min(self.rows, i + 2)):
                            for y in range(max(0, j - 1), min(self.cols, j + 2)):
                                if self.board[x][y] == "M":
                                    count += 1
                        self.board[i][j] = count

        def create_widgets(self):
            for i in range(self.rows):
                for j in range(self.cols):
                    btn = tk.Button(self.master, width=3, height=1)
                    btn.grid(row=i, column=j)
                    btn.bind('<Button-1>', lambda event, r=i, c=j: self.on_left_click(r, c))
                    btn.bind('<Button-3>', lambda event, r=i, c=j: self.on_right_click(r, c))
                    self.buttons[i][j] = btn

        def on_left_click(self, row, col):
            if not self.flags[row][col]:
                if self.board[row][col] == "M":
                    self.game_over()
                elif self.board[row][col] == 0:
                    self.reveal_empty(row, col)
                else:
                    self.buttons[row][col].config(text=str(self.board[row][col]), state=tk.DISABLED)

        def reveal_empty(self, row, col):
            if 0 <= row < self.rows and 0 <= col < self.cols and self.buttons[row][col]["state"] == tk.NORMAL:
                self.buttons[row][col].config(text=str(self.board[row][col]), state=tk.DISABLED)
                if self.board[row][col] == 0:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            self.reveal_empty(row + i, col + j)

        def on_right_click(self, row, col):
            if self.buttons[row][col]["state"] == tk.NORMAL:
                if self.flags[row][col]:
                    self.buttons[row][col].config(text="", state=tk.NORMAL)
                    self.flags[row][col] = False
                else:
                    self.buttons[row][col].config(text="F")
                    self.flags[row][col] = True

        def game_over(self):
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] == "M":
                        self.buttons[i][j].config(text="*", state=tk.DISABLED)
                    else:
                        self.buttons[i][j].config(state=tk.DISABLED)
            messagebox.showinfo("Partida finalizada", "Has perdido. ¡Inténtalo de nuevo!")
            self.reset_game()

        def reset_game(self):
            for i in range(self.rows):
                for j in range(self.cols):
                    self.board[i][j] = 0
                    self.buttons[i][j].config(text="", state=tk.NORMAL)
                    self.flags[i][j] = False
            self.generate_mines()
            self.calculate_numbers()

    if __name__ == "__main__":
        root = tk.Tk()
        game = Buscaminas(root)
        root.mainloop()


iniciarPartida()