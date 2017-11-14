# import pdb


rows = 'ABCDEFGHI'
cols = '123456789'
assignments = []
currtwin = []

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


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
    boxes = cross(rows, cols)
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
    """
    Remove solved values from the string of possible values in unsolved boxes
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
            # values = assign_value(values, peer, values[peer].replace(digit,''))
    return values


def only_choice(values):
    """
    Assign a particular digit to a box if that is the only possible value left
    """
    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    unitlist = row_units + column_units + square_units
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
                # values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Eliminate solved values from peer boxes and assign single-digit possibilities as solved values
    """
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
    # If it fails the diagonal constraint
    if diagonvals(values) == False:
        return False
    # If it results in an impossible solution
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier

    # Check for the existence of naked twins
    values = naked_twins(values)

    if all(len(values[s]) == 1 for s in boxes): 
        return diagonvals(values) ## Possibly solved!

    # Prioritize DFS for naked twins if available
    if len(currtwin) > 0:
        s = currtwin[0]
        # print(s)
        del currtwin[:] # Possibly unecessary
    else:
        # Choose one of the unfilled squares with the fewest possibilities
        n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        # new_sudoku = assign_value(new_sudoku,s,value)
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def diagonvals(values):
    """
    Diagonal sudoku constraint
    """
    diag = [[],[]]

    for i in range(1,5):
        # Diagonal values except for the top row (row_units[0])
        if len(values[row_units[i][i]]) == 1:
            diag[0].append(values[row_units[i][i]])
        if len(values[row_units[-i][-i]]) == 1:
            diag[0].append(values[row_units[-i][-i]])
        if len(values[row_units[i][-i-1]]) == 1:
            diag[1].append(values[row_units[i][-i-1]])
        if len(values[row_units[-i][i-1]]) == 1:
            diag[1].append(values[row_units[-i][i-1]])

    # Also include the top row skipped previously (row_units[0])
    if len(values[row_units[0][-i]]) == 1:
        diag[1].append(values[row_units[0][-1]])
    if len(values[row_units[0][0]]) == 1:
        diag[0].append(values[row_units[0][0]])

    # Diagonal constraint fails if there are non-unique values
    if (len(diag[0]) > len(set(diag[0]))) | (len(diag[1]) > len(set(diag[1]))):
        del diag[:]
        return False
    
    del diag[:]
    return values


def naked_twins(values):
    """
    Naked twin elimination
    """
    # Get all boxes with 2 digits
    bidigit = [s for s in boxes if len(values[s]) == 2]
    # Look for naked twins. At least 2 boxes of 2-digit values to form a twin
    if len(bidigit) > 1:
        # Might need to see if it's possible to exclude checked boxes from the unitlist to avoid duplicate twins
        nkdtwin = [[b,p] for b in bidigit for p in peers[b] if values[b] == values[p]]
    else:
        # No twins found
        return values

    # If twins are found
    if len(nkdtwin) > 0:
        # print(nkdtwin)
        # pdb.set_trace()
        # Check for duplicate twins
        for twn in nkdtwin:
            if [twn[1],twn[0]] in nkdtwin:
                nkdtwin.remove(twn)
        # To be consumed by the DFS later
        currtwin.append(nkdtwin[0][0])
        for twin in nkdtwin:
            # Only 2-digit values are considered. 
            # If a twin ceases to be so due to previous rounds of elimination, we skip it.
            if len(values[twin[0]]) == 2 and len(values[twin[1]]) == 2:
                twpeers = peers[twin[0]].intersection(peers[twin[1]])
                for peer in twpeers:
                    # values = assign_value(values, peer, values[peer].replace(values[twin[0]][0],''))
                    # values = assign_value(values, peer, values[peer].replace(values[twin[0]][1],''))
                    values[peer] = values[peer].replace(values[twin[0]][0],'')
                    values[peer] = values[peer].replace(values[twin[0]][1],'')
    return values


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = reduce_puzzle(grid_values(grid))
    res = search(values)
    if res:
        return res
    else:
        return False


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    for k,v in enumerate(square_units):
        print("%s,%s" % (k, v))
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
