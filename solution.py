import pdb
import re


rows = 'ABCDEFGHI'
cols = '123456789'
assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values


def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def altsearch(values):
    "Using depth-first search and propagation, try all possible values."
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    # First, reduce the puzzle using the previous function
    values = new_naked_twins(values)
    if all(len(values[s]) == 1 for s in boxes): 
        return xconstraint(values) ## Possibly solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku = assign_value(new_sudoku,s,value)
        attempt = altsearch(new_sudoku)
        if attempt:
            return attempt


def xconstraint(values):
    display(values)
    diag_left = []
    diag_right = []
    for i in range(1,5):
        diag_left.append(values[row_units[i][i]])
        diag_left.append(values[row_units[-i][-i]])
        diag_right.append(values[row_units[i][-i-1]])
        diag_right.append(values[row_units[-i][i-1]])

    # Add back the missing row_units[0]
    diag_right.append(values[row_units[0][-1]])
    diag_left.append(values[row_units[0][0]])
    # Diagonal constraint checks. Each set will have 9 digits if the numbers are unique
    print(set(diag_left))
    print(set(diag_right))
    # pdb.set_trace()
    if len(set(diag_right)) + len(set(diag_left)) == 18:
        return values
    else:
        return False


def initxvalues(values):
    diag = [[],[]]
    ind = [0,1]

    for i in range(1,5):
        if len(values[row_units[i][i]]) == 1:
            diag[0].append(values[row_units[i][i]])
        if len(values[row_units[-i][-i]]) == 1:
            diag[0].append(values[row_units[-i][-i]])
        if len(values[row_units[i][-i-1]]) == 1:
            diag[1].append(values[row_units[i][-i-1]])
        if len(values[row_units[-i][i-1]]) == 1:
            diag[1].append(values[row_units[-i][i-1]])

    # Add back the missing row_units[0]
    if len(values[row_units[0][-i]]) == 1:
        diag[1].append(values[row_units[0][-1]])
    if len(values[row_units[0][0]]) == 1:
        diag[0].append(values[row_units[0][0]])
    return dict(zip(ind,diag))


def new_naked_twins(values):
    bidigit = [s for s in boxes if len(values[s]) == 2]
    # Look for naked twins
    if len(bidigit) > 0:
        nkdtwin = [[b,p] for b in bidigit for p in peers[b] if values[b] == values[p]]
    else:
        # No twins found
        return values

    if len(nkdtwin) > 0:
        # Eliminate the first pair of twins
        for i in range(0,9):
            # Row twins
            if nkdtwin[0][0] in row_units[i] and nkdtwin[0][1] in row_units[i]:
                row_peers = list(set(row_units[i])-set(nkdtwin[0]))
                for rp in row_peers:
                    values = assign_value(values,rp,values[rp].replace(values[nkdtwin[0][0]][0],''))
                    values = assign_value(values,rp,values[rp].replace(values[nkdtwin[0][0]][1],''))
            # Column twins
            if nkdtwin[0][0] in column_units[i] and nkdtwin[0][1] in column_units[i]:
                col_peers = list(set(column_units[i])-set(nkdtwin[0]))
                for cp in col_peers:
                    values = assign_value(values,cp,values[cp].replace(values[nkdtwin[0][0]][0],''))
                    values = assign_value(values,cp,values[cp].replace(values[nkdtwin[0][0]][1],''))
            # Square twins
            if nkdtwin[0][0] in square_units[i] and nkdtwin[0][1] in square_units[i]:
                sq_peers = list(set(square_units[i])-set(nkdtwin[0]))
                for sq in sq_peers:
                    values = assign_value(values,sq,values[sq].replace(values[nkdtwin[0][0]][0],''))
                    values = assign_value(values,sq,values[sq].replace(values[nkdtwin[0][0]][1],''))
    return values


if __name__ == '__main__':
    boxes = cross(rows, cols)

    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    unitlist = row_units + column_units + square_units
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    twin_sudoku_grid = '1.4.9..68956.18.34..84.695151.....868..6...1264..8..97781923645495.6.823.6.854179'

    values = grid_values(diag_sudoku_grid)
    initdiag = initxvalues(values)
    values = reduce_puzzle(values)
    display(values)

    res = altsearch(values)
    if res:
        display(res)
    # print("\n")
    # try:
    #     display(solve(diag_sudoku_grid))
    # except:
    #     print("Solution not found")

    ## FOR SUBMISSION ##
    # for k,v in enumerate(square_units):
    #     print("%s,%s" % (k, v))
    # try:
    #     from visualize import visualize_assignments
    #     visualize_assignments(assignments)

    # except SystemExit:
    #     pass
    # except:
    #     print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
