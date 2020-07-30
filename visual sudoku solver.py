# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 20:58:51 2020

@author: senor
"""

from scrapy import Selector
import numpy as np, requests, collections, itertools
url = 'http://www.menneske.no/sudoku/eng/showpuzzle.html?number=2079924'
print('url working:', requests.get(url).ok)
html = requests.get(url).content
sel = Selector(text=html)
xpath = '//*[@id="bodycol"]/div[2]/div/table//*[@class="grid"]/*/text()'

sudoku = np.array([0 if i == '\xa0' else int(i) for i in sel.xpath(xpath).extract()]).reshape(9, 9).astype(object) #changed to object
sudoku_replica = sudoku * 1

sectors = [sudoku_replica[rows*3:rows*3+3, cols*3:cols*3+3] for rows in range(3) for cols in range(3)]


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

original_table = sudoku_replica * 1


def replica_updater(row, col, solution):
    print('a')
    sudoku[row, col] = solution
    sudoku_replica[row, col] = solution
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
    for pos, cell in enumerate(sudoku_replica.flatten()):
        if type(cell)==list and len(cell)==1:
            row = pos//9
            col = pos%9
            solution = int(cell[0])
            #np.flatten() does not work with index, some issue with my code
            #but also issues with np.int32 == [np.int32] returns '[ True]'
            #overall it is unreliable
            #fixes:
                #used int as opposed to np.int32
                #used enumerate and pos
            
            replica_updater(row, col, solution)
            return(difficulty_1(True))
    return solve


def difficulty_2(solve):
    
    for row, row_values in enumerate(sudoku_replica):
        unique_row_values = [possible_values for cell in row_values if isinstance(cell,list) for possible_values in cell]
        unique_row_values, counts = np.unique(unique_row_values, return_counts=True)
        unique_row_values = unique_row_values[counts==1]
        if len(unique_row_values) != 0:
            for solution in unique_row_values:
                for col, cell in enumerate(row_values):
                    if type(cell)==list and solution in cell:
                        
                        replica_updater(row, col, int(solution))
                        return(difficulty_2(True))
    
    for col, col_values in enumerate(sudoku_replica.T):
        unique_col_values = [possible_values for cell in col_values if isinstance(cell,list) for possible_values in cell]
        unique_col_values, counts = np.unique(unique_col_values, return_counts=True)
        unique_col_values = unique_col_values[counts==1]
        if len(unique_col_values) != 0:
            for solution in unique_col_values:
                for row, cell in enumerate(col_values):
                    if type(cell)==list and solution in cell:
                        
                        replica_updater(row, col, int(solution))
                        return(difficulty_2(True))
    
    for sector_num, sector_values in enumerate(sectors):
        unique_sector_values = [possible_values for cell in sector_values.flatten() if isinstance(cell,list) for possible_values in cell]
        unique_sector_values, counts = np.unique(unique_sector_values, return_counts=True)
        unique_sector_values = unique_sector_values[counts==1]
        if len(unique_sector_values) != 0:
            for solution in unique_sector_values:
                for pos, cell in enumerate(sector_values.flatten()):
                    if type(cell)==list and solution in cell:
                        row, col = pos//3 + sector_num//3*3, pos%3 + sector_num%3*3
                        
                        replica_updater(row, col, int(solution))
                        return(difficulty_2(True))
    return solve


def main():
    
    if list(sudoku.flatten()).count(0) == 0:
        print('sudoku solved')
    
    difficulty_1(False)
    difficulty_2(False)
    
    pass


if __name__ == '__main__':
    main()


puzzle_num = sel.xpath('//*[@id="bodycol"]/div[2]/div/text()[1]').extract()
url = 'http://www.menneske.no/sudoku/eng/solution.html?number=' + puzzle_num[0].split()[3]
xpath = '//*[@id="bodycol"]/div[2]/div/table//*[@class="grid"]/*/text()'
print('url working:', requests.get(url).ok)
html = requests.get(url).content
sel = Selector(text=html)
sudoku_solution = np.array(sel.xpath(xpath).extract(), dtype=int).reshape(9,9)
if np.array_equal(sudoku, sudoku_solution) == True: print('solution is correct')
else: print('solution is incorrect, puzzle num:', puzzle_num[0].split()[3])
