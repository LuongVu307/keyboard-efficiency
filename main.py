import pygame
import sys
import random

from autotype import Autotyper

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 1000, 600 

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keyboard simulator")

large_font = pygame.font.Font('freesansbold.ttf', 16)
test_font = pygame.font.SysFont("Courier", 28)
title_font = pygame.font.Font('freesansbold.ttf', 48)
start_font = pygame.font.Font('freesansbold.ttf', 32)

class Key:
    def __init__(self, screen, values, height, width):
        self.values = values
        self.height = height
        self.width = width
        self.screen = screen
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.pressed = False
        self.unpressed = True

    def draw(self, X, Y):
        self.rect.x = X
        self.rect.y = Y
        rect_color = pygame.Color("Black") if self.pressed == False else pygame.Color("Grey")
        pygame.draw.rect(self.screen, rect_color, self.rect)
        pygame.draw.rect(self.screen, pygame.Color("Green"), self.rect, 3)
        if len(self.values) == 1:
            text = large_font.render(self.values, True, pygame.Color("White"))
            self.screen.blit(text, (self.rect.x+5, self.rect.y+5))
        elif len(self.values) == 2:
            text1 = large_font.render(self.values[1], True, pygame.Color("White"))
            text0 = large_font.render(self.values[0], True, pygame.Color("White"))
            self.screen.blit(text1, (self.rect.x+5, self.rect.y+5))
            self.screen.blit(text0, (self.rect.x+5, self.rect.y+50-15))
        else:
            text = large_font.render(self.values, True, pygame.Color("White"))
            self.screen.blit(text, (self.rect.x+ 5, self.rect.y+ 5))

class Test:
    def __init__(self, screen):
        self.rect = pygame.Rect(0, 0, 900, 50)
        self.current_rect = pygame.Rect(450, 60, 15, 4)
        self.screen = screen

    def draw(self, X, Y):
        self.rect.x = X
        self.rect.y = Y
        self.current_rect.y = self.rect.bottom - 10
        self.current_rect.x = self.rect.width/2 + self.rect.left
        pygame.draw.rect(self.screen, pygame.Color("Black"), self.rect, 3)
        pygame.draw.rect(self.screen, pygame.Color("Red"), self.current_rect)

    def update(self, text, typed):
        for count, char in enumerate(text):
            if count < len(typed):
                if text[count] == typed[count]:
                    color = "#3CB043"
                else:
                    color = "Red"
            else:
                color = "Black"
            test_text = test_font.render(char, True, pygame.Color(color))
            if (0 <= count-len(typed) <= 27) or (0 <= len(typed)-count <= 27):
                # print(len(typed), count)
                if char != " ":
                    self.screen.blit(test_text, (500+15*(count-len(typed)), 110))
                else:
                    if color != "Red":
                        color = "LightGray"
                    pygame.draw.rect(self.screen, color, (500+15*(count-len(typed))+1, 110+3, 16, 24))


def check_shift():
    for key in total:
        if key.values.lower() == "lshift" or key.values.lower() == "rshift":
            if key.pressed == True:
                return True
    return False

def get_pressed_keys():
    pressed_keys = []
    keys = pygame.key.get_pressed()
    for i in range(97, 123):
        if keys[i] == True:
            pressed_keys.append(chr(i))
    for i in range(44, 58):
        if keys[i] == True:
            pressed_keys.append(chr(i))
    if keys[1073742049] == True:
        pressed_keys.append("lshift")
    if keys[1073742053] == True:
        pressed_keys.append("rshift")
    if keys[1073741881] == True:
        pressed_keys.append("caps lock")
    if keys[13] == True:
        pressed_keys.append("enter")
    if keys[32] == True:
        pressed_keys.append("space")
    if keys[61] == True:
        pressed_keys.append("=")
    if keys[91] == True:
        pressed_keys.append("[")
    if keys[93] == True:
        pressed_keys.append("]")
    if keys[59] == True:
        pressed_keys.append(";")
    if keys[39] == True:
        pressed_keys.append("'")
    if keys[92] == True:
        pressed_keys.append("\\")
    if keys[8] == True:
        pressed_keys.append("backspace")
    

    return pressed_keys

def format_time(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    milliseconds = milliseconds % 1000
    return f'{minutes:02}:{seconds:02}:{milliseconds:03}'

def create_button(screen, text, font, color, position):
    text = font.render(text, True, color)
    text_rect = text.get_rect()
    text_rect.center = position
    pygame.draw.rect(screen, pygame.Color("White"), pygame.Rect((text_rect.x - text_rect.width*0.1, text_rect.y - text_rect.height*0.1), (text_rect.width *1.2, text_rect.height*1.2)))
    screen.blit(text, text_rect)
    

running = True
state = "menu"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == "running":
            if event.type == pygame.KEYUP:
                unpressed_key = pygame.key.name(event.key)

                match unpressed_key:
                    case "return":
                        unpressed_key = "enter"
                    case "left shift":
                        unpressed_key = "lshift"
                    case "right shift":
                        unpressed_key = "rshift"                    

                for count, key in enumerate(total):
                    if len(key.values) <= 2:
                        if (key.values[0]).lower() == unpressed_key:
                            total[count].pressed = False
                            total[count].unpressed = True
                    else:
                        if (key.values).lower() == unpressed_key:
                            total[count].pressed = False
                            total[count].unpressed = True

    screen.fill(pygame.Color("LightGray"))
    
    match state:
        case "menu":
            title = title_font.render("Keyboard Simulator", True, pygame.Color("Black"))
            title_rect = title.get_rect()
            title_rect.center = (WIDTH/2, HEIGHT/3)
            screen.blit(title, title_rect)

            start_button = start_font.render("Start", True, pygame.Color("Black"))
            start_button_rect = start_button.get_rect()
            start_button_rect.center = (WIDTH/2, HEIGHT/2)
            pygame.draw.rect(screen, pygame.Color("White"), pygame.Rect((start_button_rect.x - start_button_rect.width*0.1, start_button_rect.y - start_button_rect.height*0.1), (start_button_rect.width *1.2, start_button_rect.height*1.2)))
            screen.blit(start_button, start_button_rect)

            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                if 455 <= x <= 545 and 280 <= y <= 320:
                    state = "prepare"
        case "prepare":
            test = Test(screen)
        
            with open("text.txt", "r") as f:
                text = f.readlines()
            # testing_text = 'Hello guyes, My name is "Vu Gia Luong", and what is your? \n'
            testing_text = text[random.randint(0, len(text)-1)]

            typed = []

            QWERTY = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
                    ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
                    ["capslock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"", "Enter"],
                    ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?", "RShift",]
                    ]
            
            DVORAK = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","[{" ,"]}", "backspace"],
                    ["Tab", "'\"" ,",<" ,".>" ,"P" ,"Y" ,"F" ,"G" , "C" ,"R" ,"L" ,"/?" ,"=+", "\\|"],
                    ["capslock", "A" ,"O" ,"E" ,"U" ,"I" ,"D" , "H" , "T" ,"N" ,"S","-_", "Enter"],
                    ["LShift", ";:", "Q" ,"J" ,"K" ,"X" ,"B" ,"M" ,"W" , "V", "Z", "RShift",]
                    ]

            QWERTY_dist = [[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,14],
                           [0.8,1.8,2.8,3.8,4.8,5.8,6.8,7.8,8.8,9.8,10.8,11.8,12.8, 14.1],
                           [0.9,1.9,2.9,3.9,4.9,5.9,6.9,7.9,8.9,9.9,10.9,11.9,13.45],
                           [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,13.25]
                           ]
            DVORAK_dist = QWERTY_dist

            CHOSEN_STYLE = QWERTY
            CHOSEN_DIST = QWERTY_dist

            square_size = 55
            row1, row2, row3, row4 = [], [], [], []
            value1 = CHOSEN_STYLE[0][:-1]
            value2 = CHOSEN_STYLE[1][1:-1]
            value3 = CHOSEN_STYLE[2][1:-1]
            value4 = CHOSEN_STYLE[3][1:-1]
            
            for i, value in zip(range(13), value1):
                row1.append(Key(screen, value, square_size, square_size))

            for i, value in zip(range(12), value2):
                row2.append(Key(screen, value, square_size, square_size))

            for i, value in zip(range(11), value3):
                row3.append(Key(screen, value, square_size, square_size))

            for i, value in zip(range(10), value4):
                row4.append(Key(screen, value, square_size, square_size))



            caplock_key = Key(screen, "Caps Lock", square_size, square_size*1.8)
            enter_key = Key(screen, "Enter", square_size, square_size*2.4)
            first_shift_key = Key(screen, "LShift", square_size, square_size*2.25)
            second_shift_key = Key(screen, "RShift", square_size, square_size*2.975)
            space_key = Key(screen, "Space", square_size, square_size*6.3)
            first_special_key = Key(screen, "\\|", square_size, square_size*1.65)
            backspace_key = Key(screen, "Backspace", square_size, square_size*2.1)


            total = row1+row2+row3+row4
            total.append(caplock_key)
            total.append(first_shift_key)
            total.append(second_shift_key)
            total.append(space_key)
            total.append(enter_key)
            total.append(first_special_key)
            total.append(backspace_key)



            autotyper = Autotyper(QWERTY, QWERTY_dist)
            autotype_time = pygame.time.get_ticks()
            auto = True

            # if auto == True:
            #     testing_text = testing_text.lower()

            state = "running"
            start_time = False
        case "running":
            
            
            pressed_key = []
            if auto == True:
                cost, letter = autotyper.type_10fingers(testing_text, typed)
                # print(letter)
                # print(cost, letter)
                if (pygame.time.get_ticks() - autotype_time >= cost):
                    autotype_time = pygame.time.get_ticks()
                    pressed_key = letter
            else:
                pressed_key = get_pressed_keys()

            # print("PRESSED", pressed_key)

            if not(len(typed) >= len(testing_text)-1):
                current_time = pygame.time.get_ticks()                
            else:
                create_button(screen, "Evaluate", start_font, pygame.Color("Black"), (800, 200))#pygame.font.Font("freesansbold.tff", 32))

                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    if 715 <= x <= 885 and 180 <= y <= 220:
                        ...

                create_button(screen, "Restart", start_font, pygame.Color("Black"), (600, 200))#pygame.font.Font("freesansbold.tff", 32))

                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    if 532 <= x <= 667 and 179 <= y <= 216:
                        state = "prepare"


            if start_time == False and pressed_key:
                start_time = True
                start_ticks = pygame.time.get_ticks()
            if start_time == True:

                stopwatch = start_font.render(format_time(current_time - start_ticks), True, pygame.Color("Black"))
                screen.blit(stopwatch, (10, 10))

            for pressed in pressed_key:
                for count, key in enumerate(total):
                    if len(key.values) <= 2:
                        if (key.values[0]).lower() == pressed and total[count].unpressed == True:
                            total[count].pressed = True
                            total[count].unpressed = False
                            if check_shift():
                                if len(key.values) == 1:
                                    typed.append(key.values.upper())
                                elif len(key.values) == 2:
                                    typed.append(key.values[1])
                            else:
                                if len(key.values) == 1:
                                    typed.append(key.values.lower())
                                elif len(key.values) == 2:
                                    typed.append(key.values[0])
                    else:
                        if (key.values).lower() == pressed and total[count].unpressed == True:
                            total[count].pressed = True
                            if key.values.lower() == "space":
                                typed.append(" ")
                                total[count].unpressed = False
                            if key.values.lower() == "backspace":
                                if len(typed) > 0:
                                    typed.pop(-1)
                                    total[count].unpressed = False

                if auto == True:
                    for unpressed_key in letter: 
                        for count, key in enumerate(total):
                            if len(key.values) <= 2:
                                if (key.values[0]).lower() == unpressed_key:
                                    total[count].pressed = False
                                    total[count].unpressed = True
                            else:
                                if (key.values).lower() == unpressed_key:
                                    total[count].pressed = False
                                    total[count].unpressed = True



            pygame.draw.rect(screen, pygame.Color("BLACK"), (52, 250, 885, 300+3), 5)

            for j, value in enumerate(row1):
                if not ((j == 13 or j == 14)):
                    value.draw(52 + j*(square_size+3) + 5 + 3, 250 + 5 + 3)
            
            for j, value in enumerate(row2):
                value.draw(52*1.5 + (j+1)*(square_size+3) + 5 + 3, 250 + 55 + 3 + 5 + 3)
            
            for j, value in enumerate(row3):
                value.draw(52*1.8 + (j+1)*(square_size+3) + 5 + 3, 250 + (55 + 3)*2 + 5 + 3)
            
            for j, value in enumerate(row4):
                value.draw(52*2.3 + (j+1)*(square_size+3) + 5 + 3, 250 + (55 + 3)*3 + 5 + 3)
            
            caplock_key.draw(52 + 5 + 3/1.8, 250 + (55 + 3)*2 + 5 + 3)
            enter_key.draw(52*1.8 + (11+1)*(square_size+3) + 5 + 3, 250 + (55 + 3)*2 + 5 + 3)
            first_shift_key.draw(52 + 5 + 3, 250 + (55 + 3)*3 + 5 + 3)
            second_shift_key.draw(52*2.3 + (10+1)*(square_size+3) + 5 + 3, 250 + (55 + 3)*3 + 5 + 3)
            space_key.draw(52*2.6 + (2+1)*(square_size+3) + 5 + 3, 250 + (55 + 3)*4 + 5 + 3)
            first_special_key.draw(52*1.5 + (12+1)*(square_size+3) + 5 + 3, 250 + 55 + 3 + 5 + 3)
            backspace_key.draw(52 + 13*(square_size+3) + 5 + 3, 250 + 5 + 3)


            test.draw(50, 100)
            test.update(testing_text[:-1], typed)

            # print(typed)

                

    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)

print(testing_text)

# Quit Pygame
pygame.quit()
sys.exit()

