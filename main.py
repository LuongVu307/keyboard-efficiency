import sys
import csv
import random

import pygame
from pygame.image import load
from pygame.transform import scale

from autotype import SeekHunt, Type10Finger
from evolution import generate_keyboard, process_string

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

COLEMAK_img = load("images/COLEMAK_img.png")
image_width = COLEMAK_img.get_size()[0]/5.1
image_height = COLEMAK_img.get_size()[1]/5.1
COLEMAK_img = scale(COLEMAK_img, (round(image_width), round(image_height)))

DVORAK_img = load("images/DVORAK_img.png")
DVORAK_img = scale(DVORAK_img, (round(image_width), round(image_height)))

QWERTY_img = load("images/QWERTY_img.png")
QWERTY_img = scale(QWERTY_img, (round(image_width), round(image_height)))


class Key:
    def __init__(self, screen, values, height, width):
        self.values = values
        self.height = height
        self.width = width
        self.screen = screen
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.pressed = False
        self.unpressed = True

        self.pressing_color = pygame.Color("Grey")

    def draw(self, X, Y):
        self.rect.x = X
        self.rect.y = Y
        rect_color = pygame.Color("Black") if self.pressed == False else self.pressing_color
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

def check_shift(total):
    for key in total:
        if key.values.lower() == "lshift" or key.values.lower() == "rshift":
            if key.pressed == True:
                return True
    return False

def convert_key(key):
    if len(key) == 1:
        return key.lower()
    elif len(key) == 2:
        return key[0]
    else:
        return key.lower()

def get_pressed_keys(layout_original, layout_convert):
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
    
    if layout_original != layout_convert:
        new_pressed_key = []
        for key in range(len(pressed_keys)):
            done_key = False
            for i in range(len(layout_original)):
                for j in range(len(layout_original[i])):
                    # print(pressed_keys[key], convert_key(layout_original[i][j]), convert_key(layout_convert[i][j]))
                    if convert_key(layout_original[i][j]) == pressed_keys[key]:
                        new_pressed_key.append(convert_key(layout_convert[i][j]))
                        done_key = True
                        break
                    elif pressed_keys[key] == "space":
                        new_pressed_key.append("space")
                        done_key = True
                        break

                if done_key:
                    break
        return new_pressed_key                        
                        
    return pressed_keys

def format_time(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    milliseconds = milliseconds % 1000
    return f'{minutes:02}:{seconds:02}:{milliseconds:03}'

def create_button(screen, text, font, color, position, width=0, border_radius=-1, box_color=pygame.Color("White")):
    text = font.render(text, True, color)
    text_rect = text.get_rect()
    text_rect.center = position
    pygame.draw.rect(screen, box_color, pygame.Rect((text_rect.x - text_rect.width*0.1, text_rect.y - text_rect.height*0.1), (text_rect.width *1.2, text_rect.height*1.2)))
    if width:
        pygame.draw.rect(screen, pygame.Color("Black"), pygame.Rect((text_rect.x - text_rect.width*0.1, text_rect.y - text_rect.height*0.1), (text_rect.width *1.2, text_rect.height*1.2)), width=width, border_radius=border_radius)
    screen.blit(text, text_rect)

def create_text(screen, text, font, color, position):
    text_ = font.render(f"{text}", True, pygame.Color(f"{color}"))
    text_rect = text_.get_rect()
    text_rect.center = position
    screen.blit(text_, text_rect)

def draw_input_box(screen, input_box, text, font, active, color_active, color_inactive):
    color = color_active if active else color_inactive

    txt_surface = font.render(text, True, color)
    
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    
    pygame.draw.rect(screen, color, input_box, 2)

def handle_input_events(event, input_box, active, text):
    # Handle mouse click events
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Toggle active state if input box is clicked
        if input_box.collidepoint(event.pos):
            active = not active
        else:
            active = False
    
    # Handle key events
    if event.type == pygame.KEYDOWN:
        if active:
            # if event.key == pygame.K_RETURN:
            #     text = ''  # Clear the input box
            if event.key == pygame.K_BACKSPACE:
                text = text[:-1]  # Remove the last character
            else:
                text += event.unicode  # Add the typed character
    
    return active, text


def create_simulation(mode):
    running = True
    state = "start"
    mouse_down = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                # print("BRUH")
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


                    # print(unpressed_key)
                    if CHOSEN_STYLE != QWERTY:
                        new_unpressed_key = ""
                        done_key = False
                        for i in range(len(QWERTY)):
                            for j in range(len(QWERTY[i])):
                                # print(print(unpressed_key, convert_key(QWERTY[i][j]), convert_key(CHOSEN_STYLE[i][j])))
                                if convert_key(QWERTY[i][j]) == unpressed_key:
                                    new_unpressed_key = convert_key(CHOSEN_STYLE[i][j])
                                    done_key = True
                                    break
                                elif unpressed_key == "space":
                                    new_unpressed_key = "space"
                                    done_key = True
                                    break
                            if done_key:
                                break
                        unpressed_key = new_unpressed_key                        
                        
                    for count, key in enumerate(total):
                        if len(key.values) <= 2:
                            if (key.values[0]).lower() == unpressed_key:
                                total[count].pressed = False
                                total[count].unpressed = True
                        else:
                            if (key.values).lower() == unpressed_key:
                                total[count].pressed = False
                                total[count].unpressed = True
                if pygame.mouse.get_pressed()[0] and mouse_down == False:
                    mouse_down = True
                    x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    # print(x, y)
                    if 90 <= x <= 210 and 180 <= y <= 220:
                        state = "start"
                    if (len(typed) >= len(testing_text)-1):
                        if 715 <= x <= 885 and 180 <= y <= 220:
                            wps = round(len(testing_text.split())/((current_time - start_ticks)/1000)*60)
                            state = "evaluate"
                        elif 532 <= x <= 667 and 179 <= y <= 216:
                            state = "prepare"

                if state == "evaluate":
                    ...

            if state == "menu":
                active, input_text = handle_input_events(event, input_box, active, input_text)
                if pygame.mouse.get_pressed()[0] and mouse_down == False:
                    mouse_down = True
                    x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    if 360 <= x <= 440 and 100 <= y <= 140:
                        if auto_message == "OFF":
                            auto_message = " ON "
                            auto = True
                        else:
                            auto_message = "OFF"
                            auto = False
                    elif 480 <= x <= 660 and 100 <= y <= 140:
                        if auto_type_message == "10 fingers":
                            auto_type_message = " 2 fingers "
                        else:
                            auto_type_message = "10 fingers"
                    elif 70 <= x <= 465 and 160 <= y <= 303:
                        state = "prepare"
                        change_text = True
                        CHOICE = "QWERTY"
                    elif 540 <= x <= 940 and 160 <= y <= 303:
                        state = "prepare"
                        change_text = True
                        CHOICE = "COLEMAK"
                    elif 70 <= x <= 465 and 380 <= y <= 525:
                        state = "prepare"
                        change_text = True
                        CHOICE = "DVORAK"
                    elif 540 <= x <= 940 and 380 <= y <= 525:
                        try:
                            with open(f"save/{input_text}.txt") as f:
                                unprocessed_keyboard = f.readlines()[0]     
                                CHOSEN_STYLE = process_string(unprocessed_keyboard)
                                # for i in CHOSEN_STYLE:
                                #     print(i)
                                # print(type(CHOSEN_STYLE), type(CHOSEN_STYLE[0]), type(CHOSEN_STYLE[0][0]))                           
                            state = "prepare"
                            change_text = True
                            CHOICE = "custom"
                        except Exception:
                            pass


        screen.fill(pygame.Color("LightGray"))
        
        match state:
            case "start":
                input_font = pygame.font.Font(None, 32)

                color_active = pygame.Color('lightskyblue3')
                color_inactive = pygame.Color('gray15')

                input_box = pygame.Rect(570, 560, 140, 32)
                active = False
                input_text = ''

                state = "menu"
                auto_message = "OFF"
                auto_type_message = "10 fingers"

                auto = False

            case "menu":
                title = title_font.render("Keyboard Simulator", True, pygame.Color("Black"))
                title_rect = title.get_rect()
                title_rect.center = (WIDTH/2, HEIGHT/10)
                screen.blit(title, title_rect)

                create_text(screen, "Auto: ", start_font, "Black", (320, 120))
                create_button(screen, auto_message, start_font, pygame.Color("Black"), (400, 120), width=3, border_radius=2)

                if auto:
                    create_button(screen, auto_type_message, start_font, pygame.Color("Black"), (570, 120), width=3)



                
                pygame.draw.rect(screen, pygame.Color("Black"), (70, 160, image_width+20, image_height+20))
                screen.blit(QWERTY_img, (80, 170))
                create_text(screen, "QWERTY Keyboard", start_font, "Black", (255, 330))

                pygame.draw.rect(screen, pygame.Color("Black"), (70, 380, image_width+20, image_height+20))
                screen.blit(DVORAK_img, (80, 390))
                create_text(screen, "DVORAK Keyboard", start_font, "Black", (255, 550))

                pygame.draw.rect(screen, pygame.Color("Black"), (540, 160, image_width+20, image_height+20))
                screen.blit(COLEMAK_img, (550, 170))
                create_text(screen, "COLEMAK Keyboard", start_font, "Black", (740, 330))
    
                pygame.draw.rect(screen, pygame.Color("Black"), (540, 380, image_width+20, image_height+20))
                pygame.draw.rect(screen, pygame.Color("White"), (550, 390, image_width, image_height))
                create_text(screen, "Simulation Keyboard", start_font, "Black", (740, 450))
                
                draw_input_box(screen, input_box, input_text, input_font, active, color_active, color_inactive)
                create_text(screen, "Simulation Name:", input_font, "Black", (650, 549))

            case "prepare":
                test = Test(screen)

                if change_text:
                    text_type = "medium"
                    if mode == "train":
                        text_type  = random.choice(["long", "short", "medium"])
                    with open(f"sample_text\\{text_type}.txt", "r") as f:
                        text = f.readlines()
                    testing_text = text[random.randint(0, len(text)-1)]
                    # testing_text = """The robot clicked disapprovingly, gurgled briefly inside its cubical interior and extruded a pony glass of brownish liquid. "Sir, you will undoubtedly end up in a drunkard's grave, dead of hepatic cirrhosis," it informed me virtuously as it returned my ID card. I glared as I pushed the glass across the table."""
                    repeat = 0

                typed = []

                QWERTY = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
                        ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
                        ["caps lock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"", "Enter"],
                        ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?", "RShift",]
                        ]
                
                DVORAK = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","[{" ,"]}", "backspace"],
                        ["Tab", "'\"" ,",<" ,".>" ,"P" ,"Y" ,"F" ,"G" , "C" ,"R" ,"L" ,"/?" ,"=+", "\\|"],
                        ["caps lock", "A" ,"O" ,"E" ,"U" ,"I" ,"D" , "H" , "T" ,"N" ,"S","-_", "Enter"],
                        ["LShift", ";:", "Q" ,"J" ,"K" ,"X" ,"B" ,"M" ,"W" , "V", "Z", "RShift",]
                        ]

                COLEMAK = [["`~", "1!", "2@", "3#", "4$", "5%", "6^", "7&", "8*", "9(", "0)", "-_", "=+", "backspace"],
                            ["Tab", "Q", "W", "F", "P", "G", "J", "L", "U", "Y", ";:", "[{", "]}", "\\|"],
                            ["Caps Lock", "A", "R", "S", "T", "D", "H", "N", "E", "I", "O", "'\"", "Enter"],
                            ["LShift", "Z", "X", "C", "V", "B", "K", "M", ",<", ".>", "/?", "RShift"]
                        ]

                dist = [[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,14],
                            [0.8, 2, 3, 4, 5 ,6 ,7, 8, 9, 10, 11, 12, 13, 14.3],
                            [0.9, 2.2 ,3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2,12.2,13.9],
                            [1.1, 2.7,3.7,4.7,5.7,6.7,7.7,8.7,9.7,10.7,11.7,13.6]
                            ]
                
                # for i in QWERTY_dist:
                #     print(i)


                if CHOICE == "QWERTY":
                    CHOSEN_STYLE = QWERTY
                    CHOSEN_DIST = dist
                elif CHOICE == "DVORAK":
                    CHOSEN_STYLE = DVORAK
                    CHOSEN_DIST = dist
                elif CHOICE == "COLEMAK":
                    CHOSEN_STYLE = COLEMAK
                    CHOSEN_DIST = dist
                else:
                    CHOSEN_DIST = dist


                # CHOSEN_STYLE = [['`~', '1!', '2@', '3#', '4$', '5%', '6^', '7&', '8*', '9(', '0)', '-_', '=+', 'backspace'], 
                #             ['Tab', 'J', 'F', 'V', ',<', 'G', '.>', 'I', 'B', ']}', ';:', 'R', 'X', '\\|'], 
                #             ['Caps Lock', 'E', 'H', 'T', 'Y', 'M', 'S', 'U', 'A', 'P', '\'"', 'Z', 'Enter'], 
                #             ['LShift', 'W', 'Q', 'C', 'L', 'K', '/?', 'D', 'O', 'N', '[{', 'RShift']]


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




                if auto_type_message == "10 fingers":

                    FINGER_POS = {"1" : (2, 1), "2" : (2, 2), "3" : (2, 3), "4" : (2, 4), "5" : (2, 7), "6" : (2, 8), "7" : (2, 9), "8" : (2, 10)}
                    FINGER_SPEED = {"1" : 20, 
                                    "2" : 25, 
                                    "3" : 30, 
                                    "4" : 35, 
                                    "5" : 35, 
                                    "6" : 30, 
                                    "7" : 25, 
                                    "8" : 20}
                    FINGER_COLOR = {"0": pygame.Color("Gray"), "1" : pygame.Color("Pink"), "2" : pygame.Color("Red"), "3" : pygame.Color("Yellow"), "4" : pygame.Color("Green"), "5" : pygame.Color("Blue"), "6" : pygame.Color("Purple"), "7" : pygame.Color("Brown"), "8" : pygame.Color("Light blue")}

                    autotyper = Type10Finger(keyboard=CHOSEN_STYLE, dist_layout = CHOSEN_DIST, finger_speed = FINGER_SPEED, starting_pos=FINGER_POS)

                elif auto_type_message == " 2 fingers ":
                    FINGER_POS = {"4" : (2, 4), "5" : (2, 7)}
                    FINGER_SPEED = {"4" : 35, "5" : 35}
                    FINGER_COLOR = {"0": pygame.Color("Gray"), "4" : pygame.Color("Green"), "5" : pygame.Color("Blue")}

                    autotyper = SeekHunt(keyboard=CHOSEN_STYLE, dist_layout = CHOSEN_DIST, finger_speed = FINGER_SPEED, starting_pos=FINGER_POS)



                autotype_time = pygame.time.get_ticks()

                # if auto == True:
                #     testing_text = testing_text.lower()

                state = "running"
                start_time = False
                capslock = False
                raw_typed = []
            case "running":
                pressed_key = []
                pressed_key = get_pressed_keys(QWERTY, CHOSEN_STYLE)
                if not auto:
                    fingers = ["0"] * len(pressed_key)
                # print("PRESSED", pressed_key)

                if not(len(typed) >= len(testing_text)-1):
                    if auto == True:
                        try:
                            # print(pygame.time.get_ticks() - autotype_time, cost*1000)
                            if (pygame.time.get_ticks() - autotype_time >= cost*1000+50):
                                cost, letter, fingers = autotyper.type(testing_text, typed, capslock)
                                autotype_time = pygame.time.get_ticks()
                                pressed_key = letter
                        except Exception:
                            cost, letter, fingers = autotyper.type(testing_text, typed, capslock)

                    current_time = pygame.time.get_ticks() 
                else:
                    create_button(screen, "Evaluate", start_font, pygame.Color("Black"), (800, 200))#pygame.font.Font("freesansbold.tff", 32))
                    create_button(screen, "Restart", start_font, pygame.Color("Black"), (600, 200))#pygame.font.Font("freesansbold.tff", 32))

                    # if pygame.mouse.get_pressed()[0] and mouse_down == False:
                    #     mouse_down = True
                    #     print(mouse_down)
                    #     x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    #     if 715 <= x <= 885 and 180 <= y <= 220:
                    #         print("BUHR")
                    #         wps = round(len(testing_text.split())/((current_time - start_ticks)/1000)*60)
                    #         state = "evaluate"
                    #     if 532 <= x <= 667 and 179 <= y <= 216:
                    #         state = "prepare"


                    
                    if mode == "train":
                        wps = round(len(testing_text.split())/((current_time - start_ticks)/1000)*60)
                        data = [CHOICE, len(testing_text), current_time - start_ticks, wps, autotyper.type_genre]
                        with open("data.csv", "a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(data)
                        if repeat == 1:
                            change_text = True
                        else:
                            change_text = False
                            repeat += 1

                        state = "prepare"
                    else:
                        change_text = True


                if start_time == False and pressed_key:
                    start_time = True
                    start_ticks = pygame.time.get_ticks()
                if start_time == True:

                    stopwatch = start_font.render(format_time(current_time - start_ticks), True, pygame.Color("Black"))
                    screen.blit(stopwatch, (10, 10))

                    if mode == "train":
                        if (current_time - start_ticks)/1000 > 500:
                            state = "prepare"

                
                
                for pressed, finger in zip(pressed_key, fingers):
                    for count, key in enumerate(total):
                        if len(key.values) <= 2:
                            if (key.values[0]).lower() == pressed and total[count].unpressed == True:
                                raw_typed.append(key.values)
                                total[count].pressed = True
                                total[count].unpressed = False
                                total[count].pressing_color = FINGER_COLOR[finger]
                                if check_shift(total):
                                    if len(key.values) == 1:
                                        typed.append(key.values.upper())
                                    elif len(key.values) == 2:
                                        typed.append(key.values[1])
                                else:
                                    if len(key.values) == 1:
                                        if capslock:
                                            typed.append(key.values.upper())
                                        else:
                                            typed.append(key.values.lower())
                                    elif len(key.values) == 2:
                                        typed.append(key.values[0])
                        else:
                            if (key.values).lower() == pressed and total[count].unpressed == True:
                                total[count].pressed = True
                                total[count].pressing_color = FINGER_COLOR[finger]
                                raw_typed.append(key.values)
                                if key.values.lower() == "space":
                                    typed.append(" ")
                                    total[count].unpressed = False
                                if key.values.lower() == "backspace":
                                    if len(typed) > 0:
                                        typed.pop(-1)
                                        total[count].unpressed = False
                                if key.values.lower() == "caps lock":
                                    if capslock == True:
                                        capslock = False
                                    else:
                                        capslock = True
                                    total[count].unpressed = False
                                    

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
                
                if auto:
                    autotyper.draw(screen, FINGER_COLOR)

                create_button(screen, " Back ", start_font, pygame.Color("Black"), (150, 200), width=4, box_color=pygame.Color("SkyBlue"))

                
                
                # print(raw_typed)
            case "evaluate":
                WPS_text = start_font.render(f"Words per second: {str(wps)} (wps)", True, pygame.Color("Black"))
                screen.blit(WPS_text, (50, 50))

                create_button(screen, "Back", start_font, pygame.Color("SkyBlue"), (150, HEIGHT - 50))

                if pygame.mouse.get_pressed()[0] and mouse_down == False:
                    mouse_down = True
                    x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                    if 105 <= x <= 195 and 530 <= y <= 570:
                        state = "running"

                    

        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(60)

    # Quit Pygame
    pygame.quit()
    sys.exit()




def main():
    create_simulation(mode="")




if __name__ == "__main__":
    main()