import tkinter as tk
import time
import threading
import GamePlay as gp


class DrawBoard(object):
    def __init__(self, master,G):
        master.title("Checkers")
        canv_frame=tk.Frame(master)
        canv_frame.pack()
        self.canvas= tk.Canvas(canv_frame, width=10, height=60, bg="gray")
        self.canvas.pack(padx=10, pady=10)
        self.trace = G
        self.create_grid(G[0])
        self.activate(G[0])

    def create_rect(self,coord, val):
        if val==0:
            fill="white"
            self.canvas.create_rectangle(coord, fill=fill, outline="black")
        elif val == 1:
            fill = "darkblue"
            self.canvas.create_rectangle(coord, fill=fill, outline="black")
        elif val == 2:
            fill = "darkblue"
            self.canvas.create_rectangle(coord, fill=fill, outline="black")
            self.canvas.create_oval([coord[0]+20,coord[1]+20,coord[2]-20,coord[3]-20], fill="red", outline="black")
        elif val == 3:
            fill = "darkblue"
            self.canvas.create_rectangle(coord, fill=fill, outline="black")
            self.canvas.create_oval([coord[0] + 20, coord[1] + 20, coord[2] - 20, coord[3] - 20], fill="green",
                                    outline="black")
        elif val == 4:
            fill = "darkblue"
            self.canvas.create_rectangle(coord, fill=fill, outline="black")
            self.canvas.create_oval([coord[0] + 20, coord[1] + 20, coord[2] - 20, coord[3] - 20], fill="red",
                                    outline="yellow", width=5)
        else:
            fill = "darkblue"
            self.canvas.create_rectangle(coord, fill=fill, outline="black")
            self.canvas.create_oval([coord[0] + 20, coord[1] + 20, coord[2] - 20, coord[3] - 20], fill="green",
                                    outline="yellow", width=5)

    def create_row(self, vector, y_coord):
        y0, y1=y_coord
        w=100
        x0, x1=0, w
        self.canvas.configure(width=w*len(vector))
        for i in range(len(vector)):
            self.create_rect([x0,y0,x1,y1], vector[i])
            x0=x1
            x1+=w
        return

    def create_grid(self, matrix):
        yc_og= (0,100)
        yc=(0,100)
        self.canvas.configure(height=100*len(matrix))
        for vector in matrix:
            self.create_row(vector, yc)
            yc=(yc[1],yc[1]+yc_og[1])

    def update_grid(self, G):
        self.canvas.update()
        self.create_grid(G)

    def activate(self, G):
        thread=threading.Thread(target=lambda: self.move_pieces(G))
        thread.daemon=True # End thread when program is closed
        thread.start()

    def move_pieces(self, G):
        i = 0
        while True:
            try:
                time.sleep(0.5)
                G = self.trace[i]
                self.update_grid(G)
                i += 1
            except IndexError:
                break


def start_simulation(G):
    root=tk.Tk()
    root.resizable(0,0)
    DrawBoard(root,G)
    root.mainloop()

game = gp.Game()
# game.value_iteration(100)
game.load_values_from_text()
game.play_game()
grid = game.grid_states[:]
# grid = [[[0, 4, 0, 3, 0, 3, 0, 3], [3, 0, 3, 0, 3, 0, 3, 0], [0, 3, 0, 3, 0, 3, 0, 3], [1, 0, 1, 0, 1, 0, 1, 0],
#          [0, 1, 0, 1, 0, 1, 0, 1], [2, 0, 2, 0, 2, 0, 2, 0], [0, 2, 0, 2, 0, 2, 0, 2], [2, 0, 2, 0, 2, 0, 5, 0]]]

if __name__ == "__main__":
    start_simulation(grid)

