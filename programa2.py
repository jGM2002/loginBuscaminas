import tkinter as tk
from tkinter import messagebox
import random
import time
import sqlite3

class Buscaminas:
    def __init__(self, master, cursor, jugador_actual, conn):
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

        self.turno = 1
        self.start_time = None
        self.last_clicked = None
        self.conn = conn
        self.cursor = cursor
        self.jugador_actual = jugador_actual

        self.indicador_turno = tk.Label(self.master, text="Jugador 1", font=("Arial", 14))
        self.indicador_turno.grid(row=self.rows, columnspan=self.cols)
        self.contador_turno_label = tk.Label(self.master, text="Turno: 1", font=("Arial", 14))
        self.contador_turno_label.grid(row=self.rows + 1, columnspan=self.cols)

        self.cronometro_label = tk.Label(self.master, text="Tiempo: 0s", font=("Arial", 14))
        self.cronometro_label.grid(row=self.rows + 4, columnspan=self.cols)

        self.nueva_partida_button = tk.Button(self.master, text="Nueva Partida", command=self.reset_game)
        self.nueva_partida_button.grid(row=self.rows + 2, columnspan=self.cols)

        self.cerrar_button = tk.Button(self.master, text="Cerrar", command=self.cerrar_programa)
        self.cerrar_button.grid(row=self.rows + 3, columnspan=self.cols)

        self.start_time = time.time()
        self.update_cronometro()

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
                btn = tk.Button(self.master, width=3, height=1, command=lambda r=i, c=j: self.on_left_click(r, c))
                btn.grid(row=i, column=j)
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
                self.contador_turno()

    def reveal_empty(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols and self.buttons[row][col]["state"] == tk.NORMAL:
            self.buttons[row][col].config(text=str(self.board[row][col]), state=tk.DISABLED)
            if self.board[row][col] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        self.reveal_empty(row + i, col + j)
                self.contador_turno()

    def on_right_click(self, row, col):
        if self.buttons[row][col]["state"] == tk.NORMAL:
            if self.flags[row][col]:
                self.buttons[row][col].config(text="", state=tk.NORMAL)
                self.flags[row][col] = False
            else:
                self.buttons[row][col].config(text="F")
                self.flags[row][col] = True
                self.contador_turno()

    def game_over(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == "M":
                    self.buttons[i][j].config(text="*", state=tk.DISABLED)
                else:
                    self.buttons[i][j].config(state=tk.DISABLED)
        elapsed_time = time.time() - self.start_time
        messagebox.showinfo("Partida finalizada", f"Jugador {self.turno} ha perdido. ¡Inténtalo de nuevo!\nTiempo: {elapsed_time:.2f} segundos")

        if self.last_clicked:
            row, col = self.last_clicked
            self.cursor.execute("UPDATE usuarios SET partides_jugades = partides_jugades + 1 WHERE id=?",
                                (self.jugador_actual,))

            if self.board[row][col] != "M":
                self.cursor.execute("UPDATE usuarios SET partides_guanyades = partides_guanyades + 1 WHERE id=?",
                                    (self.jugador_actual,))

            self.conn.commit()
            self.reset_game()

    def reset_game(self):
        self.start_time = time.time()
        self.update_cronometro()
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j] = 0
                self.buttons[i][j].config(text="", state=tk.NORMAL)
                self.flags[i][j] = False
        self.generate_mines()
        self.calculate_numbers()
        self.update_indicador_turno()

    def contador_turno(self):
        self.turno = 3 - self.turno  # Alternar entre 1 y 2
        self.contador_turno_label.config(text=f"Turno: {self.turno}")
        self.update_indicador_turno()

    def update_indicador_turno(self):
        jugador = f"Jugador {self.turno}"
        self.indicador_turno.config(text=jugador)

    def cerrar_programa(self):
        self.master.quit()

    def update_cronometro(self):
        elapsed_time = time.time() - self.start_time
        self.cronometro_label.config(text=f"Tiempo: {elapsed_time:.2f} segundos")
        self.master.after(100, self.update_cronometro)

if __name__ == "__main__":
    conn = sqlite3.connect("usuarios.db")
    cur = conn.cursor()