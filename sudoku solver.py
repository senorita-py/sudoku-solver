# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:38:00 2020

@author: senor
"""
from scrapy import Selector
import numpy as np, requests, collections, itertools
"solved: ", "WIP: 456903, 1617502, 3149708, 2775291"
url = 'http://www.menneske.no/sudoku/eng/showpuzzle.html?number=456903'
# url = 'http://www.menneske.no/sudoku/eng/random.html?diff=7'
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
                        sudoku[row, col] = solution
                        sudoku_replica[row, col] = solution
                        
                        replica_updater(row, col, solution)
                        return(difficulty_2(True))
    
    for col, col_values in enumerate(sudoku_replica.T):
        unique_col_values = [possible_values for cell in col_values if isinstance(cell,list) for possible_values in cell]
        unique_col_values, counts = np.unique(unique_col_values, return_counts=True)
        unique_col_values = unique_col_values[counts==1]
        if len(unique_col_values) != 0:
            for solution in unique_col_values:
                for row, cell in enumerate(col_values):
                    if type(cell)==list and solution in cell:
                        sudoku[row, col] = solution
                        sudoku_replica[row, col] = solution
                        
                        replica_updater(row, col, solution)
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
                        sudoku[row, col] = solution
                        sudoku_replica[row, col] = solution
                        
                        replica_updater(row, col, solution)
                        return(difficulty_2(True))
    return solve


def difficulty_3(solve):
    
    'if values can only be in the same box inside a row/col, remove the value from cells inside the box excluding the row/col'
    
    for row, row_values in enumerate(sudoku_replica):
        unique_row_values = [possible_values for cell in row_values if isinstance(cell,list) for possible_values in cell]
        unique_row_values, counts = np.unique(unique_row_values, return_counts=True)
        unique_row_values = list(unique_row_values[counts==2]) +list(unique_row_values[counts==3])
        for value in unique_row_values:
            cols_list = [col//3 for col, cell in enumerate(row_values) if type(cell)==list and value in cell]
            if len(set(cols_list)) == 1:
                rows = [row//3*3, row//3*3+1, row//3*3+2]
                rows.remove(row)
                for pos, cell in enumerate(sudoku_replica[rows, cols_list[0]*3:cols_list[0]*3+3].flatten()):
                    if type(cell)==list and value in cell:
                        row = rows[pos//3]
                        col = cols_list[0]*3 + pos%3
                        
                        sudoku_replica[row, col].remove(value)
                        return(difficulty_3(True))
    
    for col, col_values in enumerate(sudoku_replica.T):
        unique_col_values = [possible_values for cell in col_values if isinstance(cell,list) for possible_values in cell]
        unique_col_values, counts = np.unique(unique_col_values, return_counts=True)
        unique_col_values = list(unique_col_values[counts==2]) + list(unique_col_values[counts==3])
        for value in unique_col_values:
            rows_list = [row//3 for row, cell in enumerate(col_values) if type(cell)==list and value in cell]
            if len(set(rows_list)) == 1:
                cols = [col//3*3, col//3*3+1, col//3*3+2]
                cols.remove(col)
                for pos, cell in enumerate(sudoku_replica[rows_list[0]*3:rows_list[0]*3+3, cols].flatten()):
                    if type(cell)==list and value in cell:
                        row = rows_list[0]*3 + pos//2
                        col = cols[pos%2]
                        
                        sudoku_replica[row, col].remove(value)
                        return(difficulty_3(True))
    
    'if inside a box, a value can only be inside a row/col, remove the value from cells inside the row/col excluding the box'
    
    for sector_num, sector_values in enumerate(sectors):
        unique_sector_values = [possible_values for cell in sector_values.flatten() if isinstance(cell,list) for possible_values in cell]
        unique_sector_values, counts = np.unique(unique_sector_values, return_counts=True)
        unique_sector_values = list(unique_sector_values[counts==2]) + list(unique_sector_values[counts==3])
        for value in unique_sector_values:
            pos_list = np.array([pos for pos, cell in enumerate(sector_values.flatten()) if type(cell)==list and value in cell])
            
            rows = pos_list//3
            if len(set(rows)) == 1:
                row = sector_num//3*3 + rows[0]
                cols = [0,1,2,3,4,5,6,7,8]
                [cols.remove(col) for col in sector_num%3*3 + pos_list%3]
                for pos, cell in enumerate(sudoku_replica[row, cols]):
                    if type(cell)==list and value in cell:
                        col = cols[pos]
                        
                        sudoku_replica[row, col].remove(value)
                        return(difficulty_3(True))
            
            cols = pos_list%3
            if len(set(cols)) == 1:
                col = sector_num%3*3 + cols[0]
                rows = [0,1,2,3,4,5,6,7,8]
                [rows.remove(row) for row in sector_num//3*3 + pos_list//3]
                for pos, cell in enumerate(sudoku_replica[rows, col]):
                    if type(cell)==list and value in cell:
                        row = rows[pos]
                        
                        sudoku_replica[row, col].remove(value)
                        return(difficulty_3(True))
    
    return solve


def difficulty_4(solve):
    
    for row, row_values in enumerate(sudoku_replica):
        counter = dict(collections.Counter([tuple(cell) for cell in row_values if isinstance(cell,list)]))
        counter = {key:value for key, value in counter.items() if value != 1}
        if len(counter.keys()) != 0:
            for repeated_cell, count in counter.items():
                if len(repeated_cell) == count:
                    for value in repeated_cell:
                        for col, cell in enumerate(row_values):
                            if type(cell)==list and cell != list(repeated_cell) and value in cell:
                                
                                sudoku_replica[row, col].remove(value)
                                return(difficulty_4(True))
    
    for col, col_values in enumerate(sudoku_replica.T):
        counter = dict(collections.Counter([tuple(cell) for cell in col_values if isinstance(cell,list)]))
        counter = {key:value for key, value in counter.items() if value != 1}
        if len(counter.keys()) != 0:
            for repeated_cell, count in counter.items():
                if len(repeated_cell) == count:
                    for value in repeated_cell:
                        for row, cell in enumerate(col_values):
                            if type(cell)==list and cell != list(repeated_cell) and value in cell:
                                
                                sudoku_replica[row, col].remove(value)
                                return(difficulty_4(True))
    
    for sector_num, sector_values in enumerate(sectors):
        sector_values = sector_values.flatten()
        counter = dict(collections.Counter([tuple(cell) for cell in sector_values if isinstance(cell,list)]))
        counter = {key:value for key, value in counter.items() if value != 1}
        if len(counter.keys()) != 0:
            for repeated_cell, count in counter.items():
                if len(repeated_cell) == count:
                    for value in repeated_cell:
                        for pos, cell in enumerate(sector_values):
                            if type(cell)==list and cell != list(repeated_cell) and value in cell:
                                row = sector_num//3*3 + pos//3
                                col = sector_num%3*3 + pos%3
                                
                                sudoku_replica[row, col].remove(value)
                                return(difficulty_4(True))
    
    return solve


def difficulty_5(solve):
    
    def test_combination(allowed, combination):
            value_set = set()
            for pos in combination:
                for value in filtered[pos]:
                    value_set.add(value)
            if len(value_set) > allowed:
                return False
            else:
                return value_set
    
    for row, row_values in enumerate(sudoku_replica):
        cols_and_values = {key:value for key, value in enumerate(row_values) if isinstance(value,list)}
        allowed = len(cols_and_values) - 1
        for num_pairs in range(3, allowed+1):
            filtered = {key:value for key, value in cols_and_values.items() if len(value) <= num_pairs}
            if len(filtered) >= num_pairs:
                combinations = list(itertools.combinations(filtered.keys(), num_pairs))
                for combination in combinations:
                    value_set = test_combination(num_pairs, combination)
                    if value_set:
                        not_cols = [col for (col, cell) in enumerate(row_values) if isinstance(cell,list) and col not in combination]
                        for cell, col in zip(sudoku_replica[row, not_cols], not_cols):
                            for value in value_set:
                                if value in cell:
                                    sudoku_replica[row, col].remove(value)
                                    return(difficulty_5(True))
        pass
    
    for col, col_values in enumerate(sudoku_replica.T):
        rows_and_values = {key:value for key, value in enumerate(col_values) if isinstance(value,list)}
        allowed = len(rows_and_values) - 1
        for num_pairs in range(3, allowed+1):
            filtered = {key:value for key, value in rows_and_values.items() if len(value) <= num_pairs}
            if len(filtered) >= num_pairs:
                combinations = list(itertools.combinations(filtered.keys(), num_pairs))
                for combination in combinations:
                    value_set = test_combination(num_pairs, combination)
                    if value_set:
                        not_rows = [row for (row, cell) in enumerate(col_values) if isinstance(cell,list) and row not in combination]
                        for cell, row in zip(sudoku_replica[not_rows, col], not_rows):
                            for value in value_set:
                                if value in cell:
                                    sudoku_replica[row, col].remove(value)
                                    return(difficulty_5(True))
        pass
    
    for sector_num, sector_values in enumerate(sectors):
        sector_values = sector_values.flatten()
        pos_and_values = {key:value for key, value in enumerate(sector_values) if isinstance(value,list)}
        allowed = len(pos_and_values) - 1
        for num_pairs in range(3, allowed+1):
            filtered = {key:value for key, value in pos_and_values.items() if len(value) <= num_pairs}
            if len(filtered) >= num_pairs:
                combinations = list(itertools.combinations(filtered.keys(), num_pairs))
                for combination in combinations:
                    value_set = test_combination(num_pairs, combination)
                    if value_set:
                        not_pos = np.array([pos for (pos, cell) in enumerate(sector_values) if isinstance(cell,list) and pos not in combination])
                        not_rows = sector_num//3*3 + not_pos//3
                        not_cols = sector_num%3*3 + not_pos%3
                        for row, col in zip(not_rows, not_cols):
                            for value in value_set:
                                if value in sudoku_replica[row, col]:
                                    sudoku_replica[row, col].remove(value)
                                    return(difficulty_5(True))
        pass
    
    return solve


def difficulty_6(solve):
    
    for value in [1,2,3,4,5,6,7,8,9]:
        adjusted_replica = np.array([value if isinstance(cell,list) and value in cell else 0 for cell in sudoku_replica.flatten()]).reshape(9, 9)
        
        'value appears exactly twice in row'
        rows = [True if list(row).count(value)==2 else False for row in adjusted_replica]
        row_nums = [row_num for (row_num, row) in enumerate(rows) if row]
        col_nums = list()
        for row in adjusted_replica[rows]:
            col_nums.append(tuple(col_num for (col_num, col) in enumerate(row) if col))
        
        row_col_nums = dict()
        for row_num, col_num in zip(row_nums, col_nums):
            if col_num not in row_col_nums:
                row_col_nums[col_num] = []
            row_col_nums[col_num].append(row_num)
        
        'subset for dict where there is 2 rows with same cols'
        
        row_col_nums = {k:v for k, v in row_col_nums.items() if len(v)>=2}
        if row_col_nums != {}:
            
            'associated row and col'
            
            not_rows = list(row_col_nums.values())[0]
            cols = list(row_col_nums.keys())[0]
            
            'if there is value on the cols except rows'
            
            for row, row_values in enumerate(sudoku_replica[:, cols]):
                if row not in not_rows:
                    for cell, col in zip(row_values, cols):
                        if type(cell)==list and value in cell:
                            sudoku_replica[row, col].remove(value)
                            return(difficulty_6(True))
        
        
        
        'value appears exactly twice in col'
        cols = [True if list(col).count(value)==2 else False for col in adjusted_replica.T]
        col_nums = [col_num for (col_num, col) in enumerate(cols) if col]
        row_nums = list()
        for col in adjusted_replica[:, cols].T:
            row_nums.append(tuple(row_num for (row_num, row) in enumerate(col) if row))
        
        row_col_nums = dict()
        for row_num, col_num in zip(row_nums, col_nums):
            if row_num not in row_col_nums:
                row_col_nums[row_num] = []
            row_col_nums[row_num].append(col_num)
        
        'subset for dict where there is 2 cols with same rows'
        
        row_col_nums = {k:v for k, v in row_col_nums.items() if len(v)>=2}
        if row_col_nums != {}:
            
            'associated row and col'
            
            not_cols = list(row_col_nums.values())[0]
            rows = list(row_col_nums.keys())[0]
            
            for col, col_values in enumerate(sudoku_replica.T[:, rows]):
                if col not in not_cols:
                    for cell, row in zip(col_values, rows):
                        if type(cell)==list and value in cell:
                            sudoku_replica[row, col].remove(value)
                            return(difficulty_6(True))
    
    
    return(solve)


def difficulty_7(solve):
    for value in [1,2,3,4,5,6,7,8,9]:
        adjusted_replica = np.array([value if isinstance(cell,list) and value in cell else 0 for cell in sudoku_replica.flatten()]).reshape(9, 9)
        
        
        rows = [True if list(row).count(value)in [2,3] else False for row in adjusted_replica]
        if rows.count(True) >= 3:
            row_nums = [row_num for (row_num, row) in enumerate(rows) if row]
            col_nums = list()
            for row in adjusted_replica[rows]:
                col_nums.append(tuple(col_num for (col_num, col) in enumerate(row) if col))
            
            row_col_nums = dict(zip(row_nums, col_nums))
            combinations = list(itertools.combinations(row_nums, 3))
            for combination in combinations:
                combination_cols = list()
                for row in combination:
                    for col in row_col_nums[row]:
                        combination_cols.append(col)
                
                combination_cols, counts = np.unique(combination_cols, return_counts=True)
                not_cols = combination_cols[counts!=1]
                
                if len(not_cols) == 3 and len(combination_cols) == 3: #if 3 repeated cols and 3 total cols (0 cols with appearing only once)
                    # rows = combination
                    # for row_values, row in zip(sudoku_replica[rows, :], rows):
                        # for col, cell in enumerate(row_values):
                            # if type(cell)==list and col not in not_cols and value in cell:
                                # sudoku_replica[row, col].remove(value)
                                # return(difficulty_7(True))
                    'check the cols instead of rows'
                    
                    rows = combination
                    for col_values, col in zip(sudoku_replica[:, not_cols].T, not_cols):
                        print(value, rows, not_cols)
                        for row, cell in enumerate(col_values):
                            if type(cell)==list and row not in rows and value in cell:
                                print(cell, value)
                                pass
                            
                    # print(rows, not_cols)
                    # print(4 in rows)
        
        
    #     # cols = [True if list(col).count(value)in [2,3] else False for col in adjusted_replica.T]
    #     # if cols.count(True) >= 3:
    #     #     col_nums = [col_num for (col_num, row) in enumerate(cols) if col]
    #     #     row_nums = list()
    #     #     for col in adjusted_replica[:, cols].T:
    #     #         row_nums.append(tuple(row_num for (row_num, row) in enumerate(col) if row))
            
    #     #     row_col_nums = dict(zip(col_nums, row_nums))
            
    #     #     print(row_col_nums)
    
    print('\n\n\n')
    pass



def main():
    
    if len(sudoku[sudoku==0]) == 0:
        print('sudoku solved')
        return
    
    solve_1 = difficulty_1(False) # single solution
    
    solve_2 = difficulty_2(False) # single cell
    
    solve_3 = difficulty_3(False) # single box
    
    solve_4 = difficulty_4(False) # disjoint subsets
    
    solve_5 = difficulty_5(False) # disjoint chains
    
    solve_6 = difficulty_6(False) # x wing
    
    solve_7 = difficulty_7(False) # swordfish
    
    
    if True in [solve_1, solve_2, solve_3, solve_4, solve_5, solve_6, solve_7]:
        return(main())
    
    print('finished, but not solved')
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
