import pygame
from maze import CreateMaze
import random
import time

pygame.display.init()
screen = pygame.display.set_mode((1920,1080))
clock = pygame.time.Clock()
running = True
width = 89
height = 49 
CellSize = 20
dt = 0
move_delay = 0.1  
last_move_time = 0
def Reset():
    MazeData = CreateMaze(width,height)
    Path =[pos for pos, val in MazeData.items() if val == 0]
    Edge = [ (x, y) for (x, y), val in MazeData.items() if val == 1 and (x == 0 or x == width - 1 or y == 0 or y == height - 1)]
    PathNextToEdge = []
    for (ex,ey) in Edge:
        neighbors = [(ex+1, ey), (ex-1, ey), (ex, ey+1), (ex, ey-1)]
        for nx, ny in neighbors:
            if (nx, ny) in Path and (nx, ny) not in Edge:
                PathNextToEdge.append((ex, ey))
    Start, End = random.sample(PathNextToEdge, 2)
    MazeData[Start] = 0
    MazeData[End] = 0
    player_pos = list(Start)
    return MazeData, Start, End, player_pos

MazeData, Start, End, player_pos = Reset()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()
    if current_time - last_move_time > move_delay:
        keys = pygame.key.get_pressed()
        
        new_x, new_y = player_pos[0], player_pos[1]
        moved = False

        if keys[pygame.K_w]: 
            new_y -= 1; moved = True
        elif keys[pygame.K_s]: 
            new_y += 1; moved = True
        elif keys[pygame.K_a]: 
            new_x -= 1; moved = True
        elif keys[pygame.K_d]: 
            new_x += 1; moved = True

        if moved:
            if MazeData.get((new_x, new_y)) == 0:
                player_pos = [new_x, new_y]
            last_move_time = current_time


    screen.fill("gray")

    for (x,y), value in MazeData.items():
        rect = pygame.Rect(70+(x * CellSize), 50+ (y* CellSize), CellSize, CellSize)

        if value == 0:
            color = ("white")
        else :
            color = ("black")

        if (x,y) == Start:
            color = ("green")
        elif (x,y) == End:
            color = ("red")
    
        pygame.draw.rect(screen, color, rect)
    
    player_rect = pygame.Rect(70 + (player_pos[0] * CellSize), 50 + (player_pos[1] * CellSize), CellSize, CellSize)
    pygame.draw.rect(screen, "blue", player_rect)

    if tuple(player_pos) == End:
        MazeData, Start, End, player_pos = Reset()
        last_move_time = time.time()

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
