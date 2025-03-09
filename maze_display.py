import pygame
def generate_display_cells(rdicts, maze_grid):
    display_cell_grid = []

    for x, column in enumerate(maze_grid):
        new_column = []
        for y, cell in enumerate(column):
            # Handle row
            rindex = cell["row"]
            if rindex:
                right = rdicts["row"][rindex]["head"] == (x, y) # whether it is a head
            else:
                right = True

            # Handle column
            cindex = cell["col"]
            #is_head = False
            if cindex:
                bottom = rdicts["col"][cindex]["head"] == (x, y) # whether it is a head
            else:
                bottom = True

            new_column.append([bottom, right])

        display_cell_grid.append(new_column)

    return display_cell_grid

def display_display_cell_grid(display_cell_grid, surface, width, height, stroke_width):
    # Draw big bounding box
    pygame.draw.rect(surface, (0, 0, 0), [0, 0, width, height], stroke_width)

    # Draw maze cells
    cell_width = (width-stroke_width)/len(display_cell_grid)
    cell_height = (height-stroke_width)/len(display_cell_grid[0])
    for x, column in enumerate(display_cell_grid):
        for y, cell in enumerate(column):
            bottom, right = cell
            if bottom:
                pygame.draw.line(surface, (0, 0, 0), [x*cell_width, (y+1)*cell_height], [(x+1)*cell_width, (y+1)*cell_height], stroke_width)
            if right:
                pygame.draw.line(surface, (0, 0, 0), [(x+1)*cell_width, y*cell_height], [(x+1)*cell_width, (y+1)*cell_height], stroke_width)
