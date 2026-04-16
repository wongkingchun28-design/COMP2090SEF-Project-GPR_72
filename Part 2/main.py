import pygame
from maze import CreateMaze
import random
import time
from search import search_road

pygame.init()
screen = pygame.display.set_mode((1920, 1080))      
clock = pygame.time.Clock()

width, height = 89, 49 
CellSize = 20
OFFSET_X, OFFSET_Y = 70, 50

COLOR_WALL = (0, 0, 0)             
COLOR_UNSEARCHED = (255, 255, 255) 
COLOR_DEAD_END = (60, 60, 60)      
COLOR_PATH = "yellow"             
COLOR_START = "green"
COLOR_END = "red"
COLOR_PLAYER = "blue"

def Reset():            #Reset the maze and player position, return MazeData, Start, End, player_pos
    global MazeData, Start, End, player_pos, searching, search_completed, current_search_path, current_dead_ends
    searching = False
    search_completed = False
    current_search_path = []
    current_dead_ends = set()

    MazeData = CreateMaze(width, height)
    
    PathNodes = [pos for pos, val in MazeData.items() if val == 0]
    EdgeWalls = [(x, y) for (x, y), val in MazeData.items() 
                if (x == 0 or x == width-1 or y == 0 or y == height-1)]
    
    PossibleExits = []
    for (ex, ey) in EdgeWalls:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if (ex+dx, ey+dy) in PathNodes:
                PossibleExits.append((ex, ey))
                break
    
    Start, End = random.sample(PossibleExits, 2)
    MazeData[Start] = 0
    MazeData[End] = 0
    
    player_pos = list(Start)
    return MazeData, Start, End, player_pos

MazeData, Start, End, player_pos = Reset()

searching = False
search_completed = False
search_gen = None
current_search_path = []
current_dead_ends = set()

button_rect = pygame.Rect(10, 10, 160, 40)
font = pygame.font.SysFont("Microsoft JhengHei", 20)
running = True
last_move_time = 0
move_delay = 0.05

while running:          #Main game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos) and not searching and not search_completed:
                searching = True
                search_gen = search_road(MazeData, Start, End)

    if searching and search_gen:        #Advance the search algorithm by a few steps each frame, update current_search_path and current_dead_ends, set searching to False when search is complete
        try:
            for _ in range(5): 
                path, dead, found = next(search_gen)
                current_search_path, current_dead_ends = path, dead
                if found:
                    searching = False
                    search_completed = True
                    
                    for pos, val in MazeData.items():
                        if val == 0 and pos not in current_search_path:
                            current_dead_ends.add(pos)
                    break
        except StopIteration: searching = False


    current_time = time.time()
    if not searching and current_time - last_move_time > move_delay:        #Handle player movement, only allow moving to adjacent path cells that are not in current_dead_ends unless they are also in current_search_path, update last_move_time when player moves
        keys = pygame.key.get_pressed()
        nx, ny = player_pos
        moved = False
        if keys[pygame.K_w]: ny -= 1; moved = True
        elif keys[pygame.K_s]: ny += 1; moved = True
        elif keys[pygame.K_a]: nx -= 1; moved = True
        elif keys[pygame.K_d]: nx += 1; moved = True
        
        if moved:
            target = (nx, ny)
            cur = tuple(player_pos)
            can_move = False
            
            if MazeData.get(target) == 0:
                if cur in current_search_path:
                    if target in current_search_path: can_move = True
                elif cur in current_dead_ends:
                    if target in current_dead_ends or target in current_search_path: can_move = True
                else:
                    can_move = True
            
            if can_move: player_pos = [nx, ny]
            last_move_time = current_time

    screen.fill("gray")

    for (x,y), value in MazeData.items():   #Draw the maze, color cells based on their state in the search algorithm, also draw the start and end points
        rect = pygame.Rect(OFFSET_X + x * CellSize, OFFSET_Y + y * CellSize, CellSize, CellSize)
        

        color = COLOR_WALL if value == 1 else COLOR_UNSEARCHED

        if (x, y) in current_dead_ends:     
            color = COLOR_DEAD_END
        
        if (x, y) in current_search_path:
            color = COLOR_PATH

        if (x,y) == Start: color = COLOR_START
        elif (x,y) == End: color = COLOR_END
        
        pygame.draw.rect(screen, color, rect)
    

    pygame.draw.rect(screen, COLOR_PLAYER, (OFFSET_X + player_pos[0] * CellSize, OFFSET_Y + player_pos[1] * CellSize, CellSize, CellSize))

    if not searching and not search_completed:
        pygame.draw.rect(screen, (100,100,100), button_rect)
        screen.blit(font.render("Search Road", True, "white"), (button_rect.x+40, button_rect.y+8))

    if tuple(player_pos) == End:
        Reset()

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
