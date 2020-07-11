# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 20:19:12 2020

@author: senor
"""

from scrapy import Selector
import numpy as np, tkinter as tk, requests, collections, itertools

class visual_sudoku():
    def __init__(self):
        self.optionwindow = tk.Tk()
        self.optionwindow.title('Option Select')
        self.optionwindow.geometry('250x400+750+100')
        self.optionwindow.minsize(250, 400)
        self.optionwindow.maxsize(250, 400)
        self.optioncanvas = tk.Canvas(self.optionwindow, width=250, height=400)
        self.optioncanvas.pack(fill=tk.BOTH)
        self.option_select()
        self.optionwindow.mainloop()
    
    
    def option_select(self):
        label_puzzle_num = tk.Label(self.optioncanvas, text='Puzzle Num:')
        label_puzzle_num.place(relx=0.4, rely=0.45, anchor=tk.E)
        text_puzzle_num = tk.Text(self.optioncanvas, height=1, width=15)
        text_puzzle_num.insert(tk.END, 'random')
        text_puzzle_num.place(relx=0.4, rely=0.45, anchor=tk.W)
        
        label_difficulty = tk.Label(self.optioncanvas, text='Difficulty:')
        label_difficulty.place(relx=0.4, rely=0.5, anchor=tk.E)
        difficulty = tk.IntVar()
        difficulty.set(1)
        option_difficulty = tk.OptionMenu(self.optioncanvas, difficulty, *list(range(1, 10)))
        option_difficulty.config(indicator=False, relief=tk.FLAT)
        option_difficulty.place(relx=0.43, rely=0.5, anchor=tk.CENTER)
        
        button_view = tk.Button(self.optioncanvas, text='View', font=('Helvetica', '20'), command=lambda: [button_view.destroy(), validate_puzzle_num(self, text_puzzle_num.get("1.0", 'end-1c'), difficulty.get())])
        button_view.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        def validate_puzzle_num(self, puzzle_num, difficulty):
            if puzzle_num == 'random':
                url = 'http://www.menneske.no/sudoku/eng/random.html?diff=' + str(difficulty)
            elif puzzle_num.isdigit() and 1 <= int(puzzle_num) <= 6913752:
                url = 'http://www.menneske.no/sudoku/eng/showpuzzle.html?number=' + str(int(puzzle_num))
            else:
                label_error = tk.Label(self.optioncanvas, text='Invalid Puzzle Number; must be "random" or an integer between 1 and 6913752 (inclusive)', fg='red', wraplength=225)
                label_error.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
                return
            self.new_window(url)
            pass        
        pass
    
    
    def new_window(self, url):
        
        self.window = tk.Tk()
        self.window.title('Sudoku')
        self.window.geometry('500x500+1000+100')
        self.window.minsize(500, 500)
        self.window.maxsize(500, 500)
        self.canvas = tk.Canvas(self.window, width=500, height=500)
        self.canvas.pack(fill=tk.BOTH)
        self.window.update()
        
        def set_gridlines():
            for pos in range(25, 500, 50):
                if (pos-25)%150 == 0:
                    self.canvas.create_line(25, pos, 475, pos, width=3)
                    self.canvas.create_line(pos, 25, pos, 475, width=3)
                    self.window.update()
                else:
                    self.canvas.create_line(25, pos, 475, pos)
                    self.canvas.create_line(pos, 25, pos, 475)
                    self.window.update()
            pass
        
        set_gridlines()
        
        html = requests.get(url).content
        sel = Selector(text=html)
        xpath = '//*[@id="bodycol"]/div[2]/div/table//*[@class="grid"]/*/text()'
        
        self.sudoku = np.array([0 if i == '\xa0' else int(i) for i in sel.xpath(xpath).extract()]).reshape(9, 9).astype(object)
        self.sudoku_replica = self.sudoku * 1
        
        self.display_sudoku(self.sudoku, 'sudoku')
        
        button_solve = tk.Button(self.optioncanvas, text='Solve', font=('Helvetica', '20'), command=lambda: self.solve())
        button_solve.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        self.window.mainloop()
        pass
    
    
    def display_sudoku(self, array, array_type):
        if array_type != 'sudoku':
            sudoku_replica_dict = dict()
            pass
        for row, row_values in enumerate(array):
            for col, cell in enumerate(row_values):
                if array_type == 'sudoku':
                    if cell != 0:
                        tk.Label(self.canvas, text=cell, font=('Helvetica, 15')).place(x=(row+1)*50, y=(col+1)*50, anchor=tk.CENTER)
                else:
                    if type(cell) == list:
                        for num in cell:
                            small_cell = tk.Label(self.canvas, text=num, font=('Helvetica, 7'))
                            small_cell.place(x=(row)*50+35+(num-1)%3*15, y=(col)*50+37+(num-1)//3*14, anchor=tk.CENTER)
                            if (row, col) not in sudoku_replica_dict: # added num
                                sudoku_replica_dict[(row, col)] = list()
                            sudoku_replica_dict[(row, col)].append([num, small_cell])
                
                self.window.update()
        
        if array_type != 'sudoku':
            return sudoku_replica_dict
        pass
    
    
    def solve(self):
        
        sudoku = self.sudoku
        sudoku_replica = self.sudoku_replica
        
        def solution_table():
            for row in range(9):
                for col, cell in enumerate(sudoku[row]):
                    if cell == 0:
                        sector = sudoku[row//3*3:row//3*3+3,col//3*3:col//3*3+3]
                        not_values = np.unique(list(sudoku[row][sudoku[row]!=0])+list(sudoku[:,col][sudoku[:,col]!=0])+list(sector[sector!=0].flatten()))
                        possible_values, counts= np.unique([1,2,3,4,5,6,7,8,9] + list(not_values), return_counts=True)
                        sudoku_replica[row, col] = list(possible_values[counts==1])
            pass
        
        solution_table()
        
        sudoku_replica_dict = self.display_sudoku(sudoku_replica, None)
        
        def main():
        
            def replica_updater(row, col, solution):
                for col2, cell in enumerate(sudoku_replica[row]):
                    if type(cell)==list and solution in cell:
                        sudoku_replica[row, col2].remove(solution)
                for row2, cell in enumerate(sudoku_replica[:,col]):
                    if type(cell)==list and solution in cell:
                        sudoku_replica[row2, col].remove(solution)
                for pos2, cell in enumerate(sudoku_replica[row//3*3:row//3*3+3,col//3*3:col//3*3+3].flatten()):
                    if type(cell)==list and solution in cell:
                        row2, col2 = row//3*3 + pos2//3, col//3*3 + pos2%3
                        sudoku_replica[row2, col2].remove(solution)
                pass
            
            def difficulty_1(solve):
                for cell in sudoku_replica.flatten():
                    if type(cell)==list and len(cell)==1:
                        row = list(sudoku_replica.flatten()).index(cell)//9
                        col = list(sudoku_replica.flatten()).index(cell)%9
                        sudoku[row, col] = cell[0]
                        sudoku_replica[row, col] = int(cell[0])
                        replica_updater(row, col, cell[0])
                        for label in sudoku_replica_dict[(row, col)]:
                            label[1].destroy()
                            pass
                        tk.Label(self.canvas, text=cell, font=('Helvetica, 15')).place(x=(row+1)*50, y=(col+1)*50, anchor=tk.CENTER)
                        return(difficulty_1(True))
                return solve
            
            solve_1 = difficulty_1(False)
            
            if solve_1:
                return(main())
            
            pass
        
        
        main()
        
        # for cell in sudoku_replica_dict.values():
            # for small_cell in cell:
                # print(small_cell)
            # pass
        
        self.window.mainloop()
        
        pass
    
    pass

my_class = visual_sudoku()
