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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    nkdtwins = []
    # Find all instances of naked twins
    boxtwins = [box for box in values.keys() if len(values[box]) == 2]

    for box in boxtwins:
        row = nrow(box)
        col = ncol(box)
        sq = nsquare(col, row)

        # Check for row twins
        if twin_in_row(values, box, row) is not None:
            if twin_in_row(values,box,row) not in nkdtwins:
                nkdtwins.append(twin_in_row(values,box,row))
        # Check for column twins
        if twin_in_col(values, box, col) is not None:
            if twin_in_col(values,box,col) not in nkdtwins:
                nkdtwins.append(twin_in_col(values,box,col))
        # Check for square twins
        if twin_in_square(values, box, sq) is not None:
            if twin_in_square(values,box,sq) not in nkdtwins:
                nkdtwins.append(twin_in_square(values,box,sq))
    display(values)
    print(nkdtwins)
    # Eliminate the naked twins as possibilities for their peers
    # This needs to be revised. During naked twin elimination, a peer twin may also be eliminated - leaving only 1 value for the twin box
    # assign_value fails when that happens
    for m, ntwin in enumerate(nkdtwins):
        tosquare = True
        # Eliminate possibilities for the row
        if ntwin[0][0] == ntwin[1][0]:
            pos = re.search(ntwin[0][0],rows).start()
            rowboxs = [r for r in row_units[pos] if r not in ntwin]
            for rb in rowboxs:
                assign_value(values,rb,values[rb].replace(values[ntwin[0]][0],""))
                assign_value(values,rb,values[rb].replace(values[ntwin[0]][1],""))
        elif ntwin[0][1] == ntwin[1][1]:
            # Eliminate possibilities for the column
            pos = re.search(ntwin[0][1],cols).start()
            colboxs = [c for c in column_units[pos] if c not in ntwin]
            for cb in colboxs:
                try:
                    assign_value(values,cb,values[cb].replace(values[ntwin[0]][0],""))
                    assign_value(values,cb,values[cb].replace(values[ntwin[0]][1],""))
                except:
                    pdb.set_trace()
        else:
            tosquare = False
            # Eliminate possibilities for the square
            for i in range(0,9):
                if ntwin[0] in square_units[i]:
                    pos = i
                    break
            squboxs = [q for q in square_units[pos] if q not in ntwin]
            for sq in squboxs:
                assign_value(values,sq,values[sq].replace(values[ntwin[0]][0],""))
                assign_value(values,sq,values[sq].replace(values[ntwin[0]][1],""))

        if tosquare:
            # Also check row twins and column twins to see if they belong in the same square
            # Perform square elimination if they are
            box_a_column = ncol(ntwin[0])
            box_a_row = nrow(ntwin[0])
            box_a_square = nsquare(box_a_column, box_a_row)
            box_b_column = ncol(ntwin[1])
            box_b_row = nrow(ntwin[1])
            box_b_square = nsquare(box_b_column, box_b_row)

            if box_a_square == box_b_square:
                # Square peers elimination
                squboxs = [q for q in square_units[box_a_square] if q not in ntwin]
                for sq in squboxs:
                    assign_value(values,sq,values[sq].replace(values[ntwin[0]][0],""))
                    assign_value(values,sq,values[sq].replace(values[ntwin[0]][1],""))

    return values

def ncol(box):
    for pos, char in enumerate(cols):
        if char == box[1]:
            return pos

def nrow(box):
    for pos, char in enumerate(rows):
        if char == box[0]:
            return pos

def nsquare(col, row):
    return int(col/3) + (int(row/3) * 3)

def twin_in_row(values, box, row):
    twinunits = []
    twinunits.append(box)
    for runit in row_units[row]:
        if values[runit] == values[box] and runit != box:
            twinunits.append(runit)
            return twinunits
    return None

def twin_in_col(values,box, col):
    twinunits = []
    twinunits.append(box)
    for cunit in column_units[col]:
        if values[cunit] == values[box] and cunit != box:
            twinunits.append(cunit)
            return twinunits
    return None

def twin_in_square(values, box, sq):
    twinunits = []
    twinunits.append(box)
    for squnit in square_units[sq]:
        if values[squnit] == values[box] and squnit not in twinunits:
            twinunits.append(squnit)
            return twinunits
    return None

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

def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier

    flag = True
    while flag:
        copy = values.copy()
        values = reduce_puzzle(values)
        if values is not False:
            values = naked_twins(values)
            if values == copy:
                flag = False
        else:
            return False

    if all(len(values[s]) == 1 for s in boxes):
        return xconstraint(values) ## Possibly solved!

    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku = assign_value(new_sudoku,s,value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def xconstraint(values):
    diag_left = []
    diag_right = []
    for i in range(1,5):
        diag_left.append(values[row_units[i][i]])
        diag_left.append(values[row_units[-i][-i]])
        diag_right.append(values[row_units[i][-i-1]])
        diag_right.append(values[row_units[-i][i-1]])

    # Missing row_units[0]
    diag_right.append(values[row_units[0][-1]])
    diag_left.append(values[row_units[0][0]])
    # Diagonal constraint checks
    if len(set(diag_right)) + len(set(diag_left)) == 18:
        return values
    else:
        return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Converts the grid to a dictionary
    values = reduce_puzzle(grid_values(grid))
    res = search(values)
    if res:
        return res
    else:
        return False


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
    display(solve(diag_sudoku_grid))
    grid_zero = grid_values(diag_sudoku_grid)
    display(grid_zero)
    print("**********************")
    try:
        display(solve(diag_sudoku_grid))
    except:
        print("Solution not found")

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
