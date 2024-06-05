
class Autotyper:
    def __init__(self, keyboard, dist_layout):
        self.keyboard = keyboard
        self.dist_layout = dist_layout
        lastfinger_speed, ringfinger_speed, middlefinger_speed, pointfinger_speed = 15*10, 14*10, 13*10, 12*10
        self.fingers = [(2, 1, lastfinger_speed), (2, 2, ringfinger_speed), (2, 3, middlefinger_speed), (2, 4, pointfinger_speed), (2, 9, pointfinger_speed), (2, 10, middlefinger_speed), (2, 11, ringfinger_speed), (2,12, lastfinger_speed)]
        self.no_shift_type = []
        self.shift_type = []
        for row in keyboard:
            for caps in row:
                self.no_shift_type.append(caps[0].lower())
                if len(caps) == 2:
                    self.shift_type.append(caps[1])
                elif len(caps) == 1:
                    self.shift_type.append(caps[0].upper())
                else:
                    self.shift_type.append(None)

                

    def findfinger(self, char):
        for row in self.keyboard:
            for string in row:
                if char.lower() in string.lower():
                    pos = (self.keyboard.index(row), row.index(string))
                    # print(pos)
                    distance = []
                    for finger in self.fingers:
                        pos_key = (pos[0], self.dist_layout[pos[0]][pos[1]])
                        pos_finger = (finger[0], self.dist_layout[finger[0]][finger[1]])
                        distance.append(((pos_key[0]-pos_finger[0])**2+ (pos_key[1]-pos_finger[1])**2)**(1/2))
                    # print(distance)
                    return distance
        



    def type_10fingers(self, text, typed, see_forward=7):
        time_cost, return_typed = [], []
        for see in range(see_forward):
            if len(typed)+see < len(text):
                char = text[len(typed)+see]
                if char in return_typed:
                    break
                if char == " ":
                    if "space" not in return_typed:
                        time_cost.append(0)
                        return_typed.append("space")
                    else:
                        break
                elif char == "\n":
                    time_cost.append(0)
                    return_typed.append(" ")
                else:
                    if char in self.no_shift_type:
                        all_dist = self.findfinger(char)
                        # print(all_dist)
                        shortest = min(all_dist)
                        finger = self.fingers[all_dist.index(shortest)]
                        time_cost.append(shortest*finger[2]+0.02*1000)
                        return_typed.append(char.lower())
                    else:
                        if time_cost:
                            break
                        else:
                            for count, value in enumerate(self.shift_type):
                                if value == char:
                                    first_char = "lshift"
                                    all_dist = self.findfinger(first_char)
                                    # print(all_dist)
                                    shortest = min(all_dist)
                                    finger = self.fingers[all_dist.index(shortest)]
                                    time_cost.append(shortest*finger[2]+0.02*1000)
                                    return_typed.append(first_char.lower())


                                    second_char = self.no_shift_type[count]
                                    all_dist = self.findfinger(second_char)
                                    # print(all_dist)
                                    shortest = min(all_dist)
                                    finger = self.fingers[all_dist.index(shortest)]
                                    time_cost.append(shortest*finger[2]+0.02*1000)
                                    return_typed.append(second_char.lower())

                                    return max(time_cost), return_typed
        
        return max(time_cost), return_typed

    
    def type_adaptive(self, text, typed):
        if len(typed) < len(text):
            char = text[len(typed)]

# QWERTY = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
#                     ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
#                     ["capslock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" ,   "K" ,"L" ,";:","'\"", "Enter"],
#                     ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" ,   ",<",".>","/?", "RShift",]
#                     ]
# QWERTY_dist = [[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,14],
#                 [0.8,1.8,2.8,3.8,4.8,5.8,6.8,7.8,8.8,9.8,10.8,11.8,12.8, 14.1],
#                 [0.9,1.9,2.9,3.9,4.9,5.9,6.9,7.9,8.9,9.9,10.9,11.9,13.45],
#                 [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,13.25]
#                 ]       



            

# typer = Autotyper(QWERTY, QWERTY_dist)
# print(typer.findfinger("lshift"))
