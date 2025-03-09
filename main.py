import pygame
import random
import time
import math
from maze_display import display_display_cell_grid, generate_display_cells
"""
Python maze generator using weighted priority queue fetching and corridor-based weighting with referential updates avoiding
expensive cascades along the actual grid matrix.
"""
canvas_width, canvas_height = 1400, 800

GENERATION_DELAY_S = 0
TARGET_LENGTH = 5

minimum = 50
frac = 1/3
POPULATION_FUNC = lambda n: math.ceil(n*frac) if n > minimum/frac else minimum

INTERMEDIATE_GRAPHICS = True
strokew = 1

maze_width = int(canvas_width/10)
maze_height = int(canvas_height/10)

print(f'Running with {TARGET_LENGTH=} {maze_width=} {maze_height=}, cells={maze_width*maze_height}')

rc_metronome = 0

current_rc_ids = {"row": 1, "col": 1}

# The actual maze grid
maze_grid = [[{"row":None, "col": None} for _ in range(maze_height)] for _ in range(maze_width)]
maze_grid[0][0] = {"row": 1, "col": 1} # Initialise top-left square

# The dictionary of rows. format: rindex: row
rc_dicts = {
"row": {1: {
    "weight": 1,
    "head": (0, 0),
    "tail": (0, 0),
    "head_alive": True,
    "tail_alive": False
}},
"col": {1: {
    "weight": 1,
    "head": (0, 0),
    "tail": (0, 0),
    "head_alive": True,
    "tail_alive": False
}}
}

def get_maze_cell(x, y):
    if 0 <= x < maze_width and 0 <= y < maze_height:
        return maze_grid[x][y]
    else:
        return None

def cell_visited(cell):
    return cell["row"] is not None

def initialise_new_rc(x: int, y: int, row_or_col: str):
    global current_rc_ids, rc_dicts
    """
    Creates a new 1-member row or column for this cell and returns its index.
    row_or_col: whether to create a row or column (either "row" or "col")
    """

    # Prerequisite variables and values
    dict_var = rc_dicts[row_or_col]
    current_rc_ids[row_or_col] += 1
    id = current_rc_ids[row_or_col] # ID of this new row/col

    # Shifts for where to check if tail/head is dead
    check_shifts = {
        "row": {"head": (1, 0), "tail": (-1, 0)},
        "col": {"head": (0, 1), "tail": (0, -1)}
    }
    cells_to_check = check_shifts[row_or_col]

    # Construct and add the new row/col
    dict_var[id] = (test:={
        "weight": 1,
        "head": (x, y),
        "tail": (x, y),
        "head_alive": (c:=get_maze_cell(x+cells_to_check["head"][0],y++cells_to_check["head"][1])) is not None and not cell_visited(c),
        "tail_alive": (c:=get_maze_cell(x+cells_to_check["tail"][0],y++cells_to_check["tail"][1])) is not None and not cell_visited(c)
    })

    return id

def connect_rc_to_new_cell(id: int, head_or_tail: str, row_or_col: str):
    global rc_dicts, maze_grid
    """
    Connect either the head or tail to a new cell.
    THIS FUNCTION ASSUMES THAT THE HEAD/TAIL IS ALIVE
    head_or_tail: string (either 'head' or 'tail'),
    row_or_col: string (either 'row' or 'col')

    This functions handles collateral checks (heads/tails killed by adding this cell)
    in a slightly confusing way:
    1. Cells to the left or right are checked by generating their co-ordinates and checking if they exist etc
    2. But cells above or below (for col) or left or right (for row) - that is, rows that
       would have the same type (row/col) of connection cut off are checked using ahead_cell
       instead because it is easier.
    """
    if not rc_dicts[row_or_col][id][head_or_tail+"_alive"]: # Quick check for invalid connections
        raise ValueError(f"Tried to connect a head/tail that was dead: the {head_or_tail} of {row_or_col}-{id}")
    # -----------------------
    # Generate prerequisites
    # ------------------------
    inverse_rc = "row" if row_or_col == "col" else "col" # Used for collateral checks
    inverse_ht = "head" if head_or_tail == "tail" else "tail"
    dict_var = rc_dicts[row_or_col]
    inverse_dict_var =  rc_dicts[inverse_rc] # Used for collateral checks
    # Generate x/y shift offsets for new/ahead cells
    shift = {
        "head": (1, 2),
        "tail": (-1, -2)
    }
    new_shift, ahead_shift = shift[head_or_tail]

    # Generate real x/y shifts. Change x for rows and y for cols.
    real_xy_shifts = {
        "row": (new_shift, 0, ahead_shift, 0),
        "col": (0, new_shift, 0, ahead_shift)
    }
    new_shift_x, new_shift_y, ahead_shift_x, ahead_shift_y = real_xy_shifts[row_or_col]

    # The new head/tail
    new_cell_coords = (dict_var[id][head_or_tail][0]+new_shift_x,
                       dict_var[id][head_or_tail][1]+new_shift_y)

    # Generate new id values for the new cell
    if row_or_col == "row": new_cell = {"row": id, "col": initialise_new_rc(*new_cell_coords, "col")}
    else:                   new_cell = {"row": initialise_new_rc(*new_cell_coords, "row"), "col": id}

    # Generate locations where to check if a head/tail has been killed because of us
    collateral_checks = {
        "row": ((0, 1), (0, -1)),
        "col": ((1, 0), (-1, 0))
    }

    collateral_cells = collateral_checks[row_or_col]

    # There is now no need to differentiate between row/col cases so we
    # can run this part indiscriminately.
    # ----------
    # Update RC and Cell values (e.g. actually connect)
    # ----------

    dict_var[id]["weight"] += 1
    # The cell in front which may cause the tail/head to be dead.
    # We use get_maze_cell to check whether it exists/is visited
    ahead_cell_coords = [dict_var[id][head_or_tail][0]+ahead_shift_x,
                               dict_var[id][head_or_tail][1]+ahead_shift_y]
    ahead_cell = get_maze_cell(*ahead_cell_coords)


    dict_var[id][head_or_tail] = new_cell_coords
    maze_grid[new_cell_coords[0]][new_cell_coords[1]] = new_cell

    if ahead_cell is None or cell_visited(ahead_cell):
        # This cell is already connected (cell-visited/"r" is not None)
        # or we're at the edge of the board (ahead_cell is None)
        # therefore this head/tail is dead
        dict_var[id][head_or_tail+"_alive"] = False

        # Additionally, this cell is also dead because we just blocked it off
        # (if it exists, that is)
        if ahead_cell is not None:
            dict_var[ahead_cell[row_or_col]][inverse_ht+"_alive"] = False

            # STORED:
            # The cell exists and is connected and
            # This if statement checks whether the cell is a head of its row/col. Right most list is list of head
            # and tail positions, and we check this against the cell's co-ordinates.
            # (new_cell_coords[0] + x, new_cell_coords[1] + y)) in [(h := rc_dicts[inverse_rc][cell[inverse_rc]])["head"],
            #                                                       h["tail"]]:
            # affected_rc = cell[inverse_rc]

    # Check if we killed any other heads/tails by connecting this new cell (collateral damage)
    for x, y in collateral_cells:
        cell = get_maze_cell(new_cell_coords[0]+x, new_cell_coords[1]+y)
        if cell is not None and cell_visited(cell):
            affected_rcindex = cell[inverse_rc]
            # If the change is positive (to the "left") then we killed a tail.
            # if it is negative we killed a head.
            head_or_tail_affected = "head" if x+y < 0 else "tail"

            # Kill the appropriate head/tail. Reason for this if statement:
            inverse_dict_var[affected_rcindex][head_or_tail_affected+"_alive"] = False

def step():
    global rc_metronome, n
    # Sort rows and columns by weight
    alive_cols = [(id, "col", item) for id, item in rc_dicts["col"].items() if item["head_alive"] or item["tail_alive"]]
    alive_rows = [(id, "row", item) for id, item in rc_dicts["row"].items() if item["head_alive"] or item["tail_alive"]]

    population = alive_cols if rc_metronome == 1 else alive_rows
    sorted_population = sorted(population, key=lambda x: -abs(TARGET_LENGTH-x[2]['weight']), reverse=True)

    if len(sorted_population) == 0: return True

    id, row_or_col, chosen_row = random.choice(sorted_population[:POPULATION_FUNC(len(sorted_population))])

    ht_options = []
    if chosen_row["head_alive"]: ht_options+=['head']
    if chosen_row["tail_alive"]: ht_options+=['tail']
    chosen_ht = random.choice(ht_options)

    connect_rc_to_new_cell(id, chosen_ht, row_or_col)

    rc_metronome ^= 1

    print(f'At step {(n:=n+1)}, samples={POPULATION_FUNC(len(sorted_population))}')


pygame.init()

pygame.display.set_caption('Maze Generator')
surface = pygame.display.set_mode((canvas_width, canvas_height))

running = True

n = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            step()

    surface.fill(pygame.Color('#ffffff'))

    if step() or INTERMEDIATE_GRAPHICS:
        display_display_cell_grid(generate_display_cells(rc_dicts, maze_grid),
                                  surface, surface.get_width(), surface.get_height(), strokew)

    pygame.display.update()
    time.sleep(GENERATION_DELAY_S)

while True: pass
