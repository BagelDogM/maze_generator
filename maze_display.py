import pygame
def generate_display_cells(rdicts, maze_grid):
    """
    Return an easier to display list of cells in [right_edge:bool, bottom_edge:bool] format for displaying
    """
    display_cell_grid = []

    for x, column in enumerate(maze_grid):
        new_column = []
        for y, cell in enumerate(column):
            rindex = cell["row"]
            # If the cell doesn't exist, then there is a right line.
            # Otherwise, the cell has a right line if it is the head of a row.
            right = not rindex or rdicts["row"][rindex]["head"] == (x, y) # whether it is a head

            cindex = cell["col"]
            # If the cell doesn't exist, then there is a bottom line.
            # Otherwise, the cell has a bottom line if is the head of a column.
            bottom = not cindex or rdicts["col"][cindex]["head"] == (x, y) # whether it is a head

            new_column.append([bottom, right])

        display_cell_grid.append(new_column)

    return display_cell_grid

def display_display_cell_grid(display_cell_grid, surface, width, height, stroke_width):
    # Draw big bounding box
    pygame.draw.rect(surface, (0, 0, 0), [0, 0, width, height], stroke_width)

    # Draw maze cells.
    # Subtract stroke width so that cells do not overlap with the bounding box.
    cell_width = (width-stroke_width)/len(display_cell_grid)
    cell_height = (height-stroke_width)/len(display_cell_grid[0])

    for x, column in enumerate(display_cell_grid):
        for y, cell in enumerate(column):
            bottom, right = cell
            # Draw lines appropriately
            if bottom:
                pygame.draw.line(surface, (0, 0, 0), [x*cell_width, (y+1)*cell_height], [(x+1)*cell_width, (y+1)*cell_height], stroke_width)
            if right:
                pygame.draw.line(surface, (0, 0, 0), [(x+1)*cell_width, y*cell_height], [(x+1)*cell_width, (y+1)*cell_height], stroke_width)
