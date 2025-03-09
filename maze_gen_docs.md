## types
# Cell:
// Does not store x and y because that is implicit in the maze grid
[row:rindex, col:cindex]

# Maze grid:
list[maze_width][maze_height]: Cell()

# Row/column:
[
  weight:n[1-maze_size]
  head: cell_xy // For row: rightmost; for column: bottommost
  tail: cell_xy // For row: leftmost;  for column: topmost
  head_alive: bool // Whether head can make its connection (i.e. that cell is unvisited)
  tail_alive: bool // Whether tail can make its connection (i.e. that cell is unvisited)
]

# Row/col dict:
// Row and column indexes can have collisions because they are never referenced ambiguously. It also makes debugging easier.
row_dict = {rindex: row, rindex: row...}
col_dict = {cindex: col, cindex: col...}

## Displaying the maze
# Display cell:
[top: bool,
bottom: bool,
left: bool,
right: bool]
