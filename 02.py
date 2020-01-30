# -*- coding: utf-8 -*-

from psychopy import visual, event, core
import pandas as pd
import filterlib as flt
import blink as blk
from pyOpenBCI import OpenBCIGanglion

import pygame
from pygame.locals import *
import random
import datetime
import time
import multiprocessing as mp


def blinks_detector(quit_program, blink_det, blinks_num, blink,):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        #print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                #connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()
                
                
####################################################
    SYMULACJA_SYGNALU = False
####################################################
    mac_adress = 'd2:b4:11:81:48:ad'
####################################################

    clock = pg.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)

if __name__ == "__main__":


    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)
    #connected = mp.Event()
    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
        )

    # rozpoczęcie podprocesu
    proc_blink_det.start()
    print('subprocess started')



#stałe
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 450
ROAD_HEIGHT = 250
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 25
scooby_POS_X = 100
scooby_POS_Y = ROAD_HEIGHT - 16
zombie_POS_Y = ROAD_HEIGHT - 20
ghost_POS_X = (scooby_POS_X- 80)
ghost_POS_Y = ROAD_HEIGHT - 46
snack_POS_X = (scooby_POS_X + 441)
snack_POS_Y = ROAD_HEIGHT - 212

pygame.init()
gameDisplay = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Scooby Doo Game')
clock = pygame.time.Clock()


scooby_list = []
scooby_list.append(pygame.image.load("graphics/scoobyjump.png")) #0
scooby_list.append(pygame.image.load("graphics/scoobyrun1.png")) #1
scooby_list.append(pygame.image.load("graphics/scoobyrun2.png")) #2
scooby_list.append(pygame.image.load("graphics/scoobyjump.png")) #3
run_indx = 1

road1 = pygame.image.load('graphics/ziemia.png')
road2 = pygame.image.load('graphics/ziemia.png')

ghost_list = []
ghost_list.append(pygame.image.load("graphics/ghost.png")) #0
ghost_list.append(pygame.image.load("graphics/ghost.png")) #1

snack_list = []
snack_list.append(pygame.image.load("graphics/snack.png")) #0
snack_list.append(pygame.image.load("graphics/snack.png")) #1

zombie_list = []
zombie_list.append(pygame.image.load("graphics/grave3.png")) #0
zombie_list.append(pygame.image.load("graphics/hand.png")) #1
zombie_list.append(pygame.image.load("graphics/grave.png")) #2
zombie_list.append(pygame.image.load("graphics/grave2.png")) #3

background = pygame.image.load('graphics/tlo.jpg')

road1_pos_x = 0
road2_pos_x = 600

pygame.mixer.init()
pygame.mixer.music.load('scooby doo.mp3')
pygame.mixer.music.play()

speed_was_up = True
clear_game = True
game_on = False
lost_game = True
scooby_jump = False
jump_height = 7
points = 0

frames_since_zombie = 0
gen_zombie_time = 50


font = pygame.font.SysFont("Times New Roman", 18)
points_font = pygame.font.SysFont('Times New Roman', 18)
startScreen = font.render('NACIŚNIJ SPACJĘ ABY ZACZĄĆ', True, WHITE, BLACK)
startScreenRect = startScreen.get_rect()
startScreenRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2-50)


gaming = True
while gaming:

    if blink.value == 1:
        if scooby_jump == False:
            game_on = True
            scooby_jump = True
            blink.value = 0
        if lost_game == True:
            time.sleep(1)
            clear_game = True
            lost_game = False
            blink.value = 0
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit_program.set()
                pygame.quit()
                quit()
                gaming = False

            if event.key == pygame.K_SPACE and scooby_jump == False:
                game_on = True
                scooby_jump = True
            if lost_game == True and event.key == pygame.K_SPACE:
                time.sleep(1)
                clear_game = True
                lost_game = False
                pygame.mixer.music.unpause()


    if clear_game == True:
        FPS = 25
        zombie_pos_x = []
        curr_zombie = []
        speed = 10
        points = 0
        clear_game = False

    gameDisplay.fill(BLACK)
    gameDisplay.blit(background,(0,0))
    gameDisplay.blit(road1, (road1_pos_x, ROAD_HEIGHT))
    if game_on == False:
        gameDisplay.blit(startScreen, startScreenRect)

    if game_on == True and lost_game == True:
        gameDisplay.blit(startScreen, startScreenRect)
        lostScreen = font.render('LICZBA SCOOBY CHRUPEK: ' + str(points), True, WHITE, BLACK)
        lostScreenRect = lostScreen.get_rect()
        lostScreenRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2-25)
        gameDisplay.blit(lostScreen, lostScreenRect)


    if speed_was_up == False and points%5 == 0:
        FPS += 3
        speed_was_up = True
    if points%5 == 1:
        speed_was_up = False

    if game_on == True:
        pointsDisplay = points_font.render('SCOOBY-CHRUPKI: ' + str(points), True, WHITE, BLACK)
        pointsRect = pointsDisplay.get_rect()
        pointsRect.center = (SCREEN_WIDTH-105, 10)
        gameDisplay.blit(pointsDisplay, pointsRect)


    if game_on == True and scooby_jump == False and lost_game == False:
        if run_indx <= 3:
            scooby = gameDisplay.blit(scooby_list[1], (scooby_POS_X, scooby_POS_Y))
            ghost = gameDisplay.blit(ghost_list[0], (ghost_POS_X, ghost_POS_Y))
            snack = gameDisplay.blit(snack_list[0], (snack_POS_X, snack_POS_Y))
            run_indx += 1
        elif run_indx < 6:
            scooby = gameDisplay.blit(scooby_list[2], (scooby_POS_X, scooby_POS_Y))
            ghost = gameDisplay.blit(ghost_list[1], (ghost_POS_X, ghost_POS_Y))
            snack = gameDisplay.blit(snack_list[1], (snack_POS_X, snack_POS_Y))
            run_indx += 1
        else:
            scooby = gameDisplay.blit(scooby_list[2], (scooby_POS_X, scooby_POS_Y))
            ghost = gameDisplay.blit(ghost_list[1], (ghost_POS_X, ghost_POS_Y))
            snack = gameDisplay.blit(snack_list[1], (snack_POS_X, snack_POS_Y))
            run_indx = 1
    elif game_on == False:
        scooby = gameDisplay.blit(scooby_list[0], (scooby_POS_X, scooby_POS_Y))
        ghost = gameDisplay.blit(ghost_list[0], (ghost_POS_X, ghost_POS_Y))
        snack = gameDisplay.blit(snack_list[0], (snack_POS_X, snack_POS_Y))

    if game_on == True and scooby_jump == True:
        if jump_height >= -7:
            going_up = 1
            if jump_height < 0:
                going_up = -1
            scooby_POS_Y -= (jump_height ** 2) * 0.8 * going_up
            ghost = gameDisplay.blit(ghost_list[1], (ghost_POS_X, ghost_POS_Y))
            snack = gameDisplay.blit(snack_list[1], (snack_POS_X, snack_POS_Y))
            jump_height -= 1
        else:
            scooby_jump = False
            jump_height = 7
        scooby = gameDisplay.blit(scooby_list[0], (scooby_POS_X, scooby_POS_Y))


    if game_on == True:
        frames_since_zombie += 1
        road1_pos_x -= speed
        if road1_pos_x <= -SCREEN_WIDTH:
            gameDisplay.blit(road2, (road2_pos_x, ROAD_HEIGHT))
            road2_pos_x -= speed
            if road2_pos_x == 0:
                road2_pos_x = 600
                road1_pos_x = 0

    if frames_since_zombie == gen_zombie_time:
        gen_zombie_time = random.randint(30, 50)
        gen_zombie_img = random.randint(0, 3)
        frames_since_zombie = 0
        curr_zombie.append([gen_zombie_img, SCREEN_WIDTH])

    for i in range(len(curr_zombie)):
        if curr_zombie[i][0] == 0 or curr_zombie[i][0] == 3:
            lower = 12
        else: lower = 0
        zombie = gameDisplay.blit(zombie_list[curr_zombie[i][0]], (curr_zombie[i][1], zombie_POS_Y+lower))
        curr_zombie[i][1] -= speed

        if curr_zombie[i][1] == 0:
            points += 1

        if scooby.colliderect(zombie):
            speed = 0
            if lost_game == False:
                pygame.mixer.music.pause()
            lost_game = True
            scooby = gameDisplay.blit(scooby_list[2], (scooby_POS_X, scooby_POS_Y))


    pygame.display.update()
    clock.tick(FPS)

proc_blink_det.join()
