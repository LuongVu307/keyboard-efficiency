import numpy as np

import pygame


class Autotyper:
    def __init__(self, keyboard, dist_layout, finger_speed, starting_pos):
        self.keyboard = keyboard
        self.dist_layout = dist_layout
        self.finger_speed = finger_speed
        self.starting_pos = starting_pos
        self.finger_pos = self.starting_pos

    def find_position(self, letter):
        position = ()
        
        for i in range(len(self.keyboard)):
            done = False
            for j in range(len(self.keyboard[i])):
                if len(self.keyboard[i][j]) <= 2:
                    if letter in self.keyboard[i][j].upper():
                        position = (i, j)
                        done = True
                else:
                    if letter == self.keyboard[i][j].upper():
                        position = (i, j)
                        done = True
            if done == True:
                break

        return position

    def find_distance(self, letter, except_finger=[], shift=False, move_finger=True):
        #Finding the letter position
        position = self.find_position(letter)

        distance = {}
        for finger in self.finger_pos:
            if finger not in except_finger:
                position_finger = self.finger_pos[finger]
                distance[finger] = np.sqrt((self.finger_pos[finger][0]-position[0])**2 + \
                                        (self.dist_layout[position_finger[0]][position_finger[1]]-\
                                            self.dist_layout[position[0]][position[1]])**2)
        
        finger = np.random.choice([key for key, value in distance.items() if value == min(distance.values())])
        if move_finger:
            self.finger_pos[finger] = position

        chosen_key = self.keyboard[position[0]][position[1]]
        chosen_letter = ""
        if len(chosen_key) == 1:
            chosen_letter = chosen_key.lower()
        elif len(chosen_key) == 2:
            chosen_letter = chosen_key[0]
        else:
            if chosen_letter.lower() == "shift":
                chosen_letter = shift
            else:
                chosen_letter = chosen_key.lower()

        # print(chosen_letter)

        return distance, finger, chosen_letter
    
    def need_shift(self, letter):
        for row in self.keyboard:
            for key in row: 
                if len(key) == 2:
                    if letter == key[1]:
                        return True
        return False
    
    def draw(self, screen, finger_color):
        for finger in self.finger_pos:
            position = self.finger_pos[finger]
            # print(finger, position)
        
            Y = position[0]
            X = self.dist_layout[position[0]][position[1]]-0.5
            pygame.draw.circle(screen, color=finger_color[finger], center=(85+58*X, 285+Y*58), radius=15)

class SeekHunt(Autotyper):
    def type(self, text, typed, capitalized):
        # print(self.finger_pos)
        typed = "".join(typed)
        letter = text[len(typed)]
        if letter == " ":
            letter = "space"
            time = 0

            return time, [letter], "0"
        if self.need_shift(letter):

            for i in range(len(self.keyboard)):
                done = False
                for j in range(len(self.keyboard[i])):
                    if letter in self.keyboard[i][j]:
                        letter = self.keyboard[i][j][0]
                        done = True
                        break
                if done == True:
                    break


            distance1, finger1, letter1 = self.find_distance("LSHIFT", move_finger=False)
            distance1_letter, finger1_letter, letter1_letter = self.find_distance(letter, except_finger=[finger1], shift="lshift", move_finger=False)

            total_distance1 = max(distance1[finger1], distance1_letter[finger1_letter])

            distance2, finger2, letter2 = self.find_distance("RSHIFT", move_finger=False)

            distance2_letter, finger2_letter, letter2_letter = self.find_distance(letter, except_finger=[finger2], shift="rshift", move_finger=False)

            total_distance2 = max(distance2[finger2], distance2_letter[finger2_letter])

            # print(distance1, distance2, distance1_letter, distance2_letter)
            if total_distance1 < total_distance2:
                distance1, finger1, letter1 = self.find_distance("LSHIFT")
                distance1_letter, finger1_letter, letter1_letter = self.find_distance(letter, except_finger=[finger1], shift="lshift")
                letter = [letter1, letter1_letter]
                finger = [finger1, finger1_letter]
                time = max(distance1[finger1]/self.finger_speed[finger1], distance1_letter[finger1_letter]/self.finger_speed[finger1_letter])

            else:
                distance2, finger2, letter2 = self.find_distance("RSHIFT")
                distance2_letter, finger2_letter, letter2_letter = self.find_distance(letter, except_finger=[finger2], shift="rshift")
                letter = [letter2, letter2_letter]
                finger = [finger2, finger2_letter]
                time = max(distance2[finger2]/self.finger_speed[finger2], distance2_letter[finger2_letter]/self.finger_speed[finger2_letter])

            return time+0.05, letter, finger

        else:
            if letter.isupper():
                if not capitalized:
                    letter = "CAPS LOCK"
                else:
                    letter = letter.upper()
            else:
                if capitalized:
                    letter = "CAPS LOCK"
                else:
                    letter = letter.upper()
            
                                                    
            distance, finger, letter = self.find_distance(letter)
            time = [distance[i]/self.finger_speed[i] for i in distance]
    
            # print(distance, letter)

            return min(time)+0.05, [letter.lower()], finger
    

class Type10Finger(Autotyper):
    def __init__(self, keyboard, dist_layout, finger_speed, starting_pos):
        super().__init__(keyboard, dist_layout, finger_speed, starting_pos)
        # print(self.finger_pos)
        if len(self.finger_pos.keys()) != 8:
            raise Exception("The number of finger has to be 8")

    def type(self, text, typed, capitalized):
        # print(self.finger_pos)
        typed = "".join(typed)
        letter = text[len(typed)]
        if letter == " ":
            letter = "space"
            time = 0

            return time, [letter], "0"
        if self.need_shift(letter):

            for i in range(len(self.keyboard)):
                done = False
                for j in range(len(self.keyboard[i])):
                    if letter in self.keyboard[i][j]:
                        letter = self.keyboard[i][j][0]
                        done = True
                        break
                if done == True:
                    break


            distance1, finger1, letter1 = self.find_distance("LSHIFT", move_finger=False)
            distance1_letter, finger1_letter, letter1_letter = self.find_distance(letter, except_finger=[finger1], shift="lshift", move_finger=False)

            total_distance1 = max(distance1[finger1], distance1_letter[finger1_letter])

            distance2, finger2, letter2 = self.find_distance("RSHIFT", move_finger=False)

            distance2_letter, finger2_letter, letter2_letter = self.find_distance(letter, except_finger=[finger2], shift="rshift", move_finger=False)

            total_distance2 = max(distance2[finger2], distance2_letter[finger2_letter])

            # print(distance1, distance2, distance1_letter, distance2_letter)
            if total_distance1 < total_distance2:
                distance1, finger1, letter1 = self.find_distance("LSHIFT")
                distance1_letter, finger1_letter, letter1_letter = self.find_distance(letter, except_finger=[finger1], shift="lshift")
                letter = [letter1, letter1_letter]
                finger = [finger1, finger1_letter]
                time = max(distance1[finger1]/self.finger_speed[finger1], distance1_letter[finger1_letter]/self.finger_speed[finger1_letter])

            else:
                distance2, finger2, letter2 = self.find_distance("RSHIFT")
                distance2_letter, finger2_letter, letter2_letter = self.find_distance(letter, except_finger=[finger2], shift="rshift")
                letter = [letter2, letter2_letter]
                finger = [finger2, finger2_letter]
                time = max(distance2[finger2]/self.finger_speed[finger2], distance2_letter[finger2_letter]/self.finger_speed[finger2_letter])

            return time+0.05, letter, finger

        else:
            if letter.isupper():
                if not capitalized:
                    letter = "CAPS LOCK"
                else:
                    letter = letter.upper()
            else:
                if capitalized:
                    letter = "CAPS LOCK"
                else:
                    letter = letter.upper()

            position = self.find_position(letter)
            if position[1] <= 1:
                include = set(["1"])
            elif position[1] == 2:
                include = set(["2"])
            elif position[1] == 3:
                include = set(["3"])
            elif position[1] <= 5:
                include = set(["4"])
            elif position[1] <= 7:
                include = set(["5"])
            elif position[1] == 8:
                include = set(["6"])
            elif position[1] == 9:
                include = set(["7"])
            else:
                include = set(["8"])
            
                                                    
            distance, finger, letter = self.find_distance(letter, except_finger=(set(self.finger_pos.keys())-include))
            time = [distance[i]/self.finger_speed[i] for i in distance]
    
            # print(distance, letter)

            return min(time)+0.05, [letter.lower()], finger
