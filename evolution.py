import pygame

from autotype import Type10Finger

import random


def generate_keyboard():
    # [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
    # ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
    # ["caps lock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"", "Enter"],
    # ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?", "RShift",]
    # ]

    keys = ["Q","W","E","R","T","Y","U","I","O","P","[{","]}",
    "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"",
    "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?",
    ]

    random.shuffle(keys)
    first, second, third = keys[:12], keys[12:23], keys[23:]

    keyboard = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
                ["Tab"] + first + ["\\|"],
                ["Caps Lock"] + second + ["Enter"],
                ["LShift"] + third + ["RShift"]           
                ]
    
    return keyboard

def process_string(individual):
    individual = individual[2:-2]
    individual = individual.split("], [")
    for count, row in enumerate(individual):
        row = row.replace("'", "")
        row = row.replace('"', "'\"")
        row = row.replace("RShift]", "RShift")
        individual[count] = row.split(", ")
    
    for i in range(len(individual)):
        for j in range(len(individual[i])):
            if individual[i][j] == '\\\'"':
                individual[i][j] = '\'"'
            elif individual[i][j] == "\\\\|":
                individual[i][j] = "\\|"
    
    return individual


class Genetic:
    def __init__(self, population_number, selection_method, selection_rate, mutation_rate, 
                 mutation_intensity, fitness_function, eltism):
        self.population = {}

        self.selection = selection_method
        self.selection_rate = selection_rate
        self.mutation_rate = mutation_rate
        self.mutation_intensity = mutation_intensity
        self.fitness_function = fitness_function
        self.eltism = eltism

        for _ in range(population_number):
            random_keyboard = str(generate_keyboard())
            if random_keyboard in self.population:
                raise Exception
            if random_keyboard not in self.population:
                self.population[random_keyboard] = 1e10

        print("Running Evolutionary Algorithms on keyboard")
        print("-------------------------------------------------------------")
        print(f"Initial population: {population_number}")
        print(f"Selection method: {selection_method.capitalize()}")
        print(f"Selection rate: {selection_rate*100}%")
        print(f"Mutation rate: {mutation_rate*100}%")
        print(f"Mutation intensity: {mutation_intensity*100}%")
        print(f"Eltism rate: {eltism*100}%")
        print("-------------------------------------------------------------")
        print()
        

    def fit(self):
        # count = 0
        for individual in self.population:
            # count += 1
            # print(count)
            # for i in process_string(individual):
            #     print(i)
            # print()
            # for i in QWERTY:
            #     print(i)
            
            # print("\n")
            self.population[individual] = self.fitness_function(process_string(individual))

        self.population = dict(sorted(self.population.items(), key=lambda x : x[1]))
        min_value = min(self.population.values())
        self.best_performance = {key : value for key, value in self.population.items() if value == min_value}

    def weight_sampling(self, population, weights, k):
        selected = []
        population_copy = population[:]
        weights_copy = weights[:]
        
        for _ in range(k):
            total = sum(weights_copy)
            probs = [w / total for w in weights_copy]
            choice = random.choices(population_copy, weights=probs, k=1)[0]
            
            selected.append(choice)
            
            index = population_copy.index(choice)
            population_copy.pop(index)
            weights_copy.pop(index)
        
        return selected

    def select(self):
        new_population_length = int(len(self.population)*self.selection_rate)
        if self.selection == "rank":
            self.new_generation = self.weight_sampling([{k: v} for k, v in self.population.items()], 
                                                k=new_population_length, 
                                                weights=list(range(len(self.population), 0, -1))
                                            )

        elif self.selection == "roulette":
            weights = self.population.values()
            weights = [1/i for i in weights]
            self.new_generation = self.weight_sampling([{k: v} for k, v in self.population.items()], k=new_population_length, 
                                                 weights=weights)
        
        elif self.selection == "tournament":
            
            def gcf(a, b):
                while b:
                    a, b = b, a % b
                return a
            
            gcf = gcf(len(self.population), new_population_length)
            if gcf == 1:
                raise Exception("Invalid selection rate")
            self.groups_number = len(self.population)//gcf
            self.winner_number = new_population_length//gcf
            
            self.new_generation = [{k: v} for k, v in self.population.items()]
            random.shuffle(self.new_generation)
            self.new_generation = [self.new_generation[i:i + self.groups_number] for i in range(0, len(self.new_generation), self.groups_number)]

            
            for count, group in enumerate(self.new_generation):
                groups = sorted(group, key=lambda d : list(d.values())[0])
                self.new_generation[count] = groups[:self.winner_number]

            self.new_generation = [item for sublist in self.new_generation for item in sublist]
        
        temp = {}
        for d in self.new_generation:
            for i, j in d.items():
                temp[i] = j

        self.new_generation = temp

    def combine(self, keyboard1, keyboard2):
        keyboard1 = process_string(keyboard1[0])
        keyboard2 = process_string(keyboard2[0])

        child = [['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '', '', ''],]

        filled = []
        for row1, row2 in zip(enumerate(keyboard1), enumerate(keyboard2)):
            for key1, key2 in zip(enumerate(row1[1]), enumerate(row2[1])):
                selected_key = random.choice([key1[1], key2[1]])
                if selected_key not in filled:
                    filled.append(selected_key)
                    child[row1[0]][key1[0]] = selected_key
                else:
                    child[row1[0]][key1[0]] = "NOTFILLED"

        unfilled = list(set([item for sublist in keyboard1 for item in sublist]) - set(filled))
        random.shuffle(unfilled)
        count = 0
        for i in range(len(child)):
            for j in range(len(child[i])):
                if child[i][j] == "NOTFILLED":
                    child[i][j] = unfilled[count]
                    count += 1
        
        return child


    def regenerate(self):
        
        self.new_generation = [{k: v} for k, v in self.new_generation.items()]
        random.shuffle(self.new_generation)
        self.new_generation = [self.new_generation[i:i + 2] for i in range(0, len(self.new_generation), 2)]

        for count, couple in enumerate(self.new_generation):
            child1 = self.combine(list(couple[0].keys()), list(couple[1].keys()))
            child2 = self.combine(list(couple[0].keys()), list(couple[1].keys()))
            self.new_generation[count] = [child1, child2]
            
        self.new_generation = [item for temp in self.new_generation for item in temp]

    def mutate(self, keyboard):
        count = int(self.mutation_intensity*20)
        while count != 0:
            i1, i2 = random.randint(1, 3), random.randint(1, 3)
            j1, j2 = random.randint(1, 12), random.randint(1, 12)
            try:
                if len(keyboard[i1][j1]) > 2 or  len(keyboard[i2][j2]) > 2:
                    raise Exception
                keyboard[i1][j1], keyboard[i2][j2] = keyboard[i2][j2], keyboard[i1][j1]
                count -= 1
            except Exception:
                pass
        return keyboard
    
    def elite(self):
        self.population = dict(sorted(self.population.items(), key=lambda x : x[1]))
        keep = list(self.population.keys())[:int(self.eltism*len(self.population))]

        self.new_generation += keep

    def simulate(self, generation, save, name):
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

        
        QWERTY_score = self.fitness_function(QWERTY)
        DVORAK_score = self.fitness_function(DVORAK)
        COLEMAK_score = self.fitness_function(COLEMAK)

        for _ in range(generation):

            print("Generation: ", _, " Population: ", len(self.population))
            print("-----------------------------------------------")
            self.fit()
            self.select()
            self.regenerate()

            for count, genes in enumerate(self.new_generation):
                if random.choices([0, 1], weights=[1-self.mutation_rate, self.mutation_rate]):
                    self.new_generation[count] = self.mutate(genes)
            self.elite()

            print(f"Generation {_}'s best performance keyboard has the average typing time of {list(self.best_performance.values())[0]}")
            print(f"Generation {_}'s keyboard has the average typing time of {sum(list(self.population.values()))/len(self.population)}")
            print(f"QWERTY has typing time of {QWERTY_score}")
            print(f"DVORAK has typing time of {DVORAK_score}")
            print(f"COLEMAK has typing time of {COLEMAK_score}")
            
            print("The keyboard layout is")
            best_keyboard = process_string(list(self.best_performance.keys())[0])
            if _ == generation-1:
                self.fit()
                save_keyboard = [process_string(i) for i in list(self.population.keys())[:save]]
                # print(save_keyboard)
                with open(f'save/{name}.txt', 'w') as file:
                    for line in save_keyboard:
                        file.write(str(line) + '\n')

            for row in best_keyboard:
                print(row)

            print()

            self.population = {str(i) : 1e10 for i in self.new_generation}


        

def fit_keyboard(keyboard, sample=54):
    # missing = set([i for row in keyboard for i in row]) - set([i for row in QWERTY for i in row])
    # print("MISSING", missing)

    # for i in keyboard:
    #     print(i)

    FINGER_POS = {"1" : (2, 1), "2" : (2, 2), "3" : (2, 3), "4" : (2, 4), "5" : (2, 7), "6" : (2, 8), "7" : (2, 9), "8" : (2, 10)}
    FINGER_SPEED = {"1" : 20, "2" : 30, "3" : 40, "4" : 50, "5" : 50, "6" : 40, "7" : 30, "8" : 20}
    FINGER_COLOR = {"0": pygame.Color("Gray"), "1" : pygame.Color("Pink"), "2" : pygame.Color("Red"), "3" : pygame.Color("Yellow"), "4" : pygame.Color("Green"), "5" : pygame.Color("Blue"), "6" : pygame.Color("Purple"), "7" : pygame.Color("Brown"), "8" : pygame.Color("Light blue")}

    dist_layout = [[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,14],
                    [0.8, 2, 3, 4, 5 ,6 ,7, 8, 9, 10, 11, 12, 13, 14.3],
                    [0.9, 2.2 ,3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2,12.2,13.9],
                    [1.1, 2.7,3.7,4.7,5.7,6.7,7.7,8.7,9.7,10.7,11.7,13.6]
                    ]
    
    autotyper = Type10Finger(keyboard=keyboard, dist_layout =dist_layout, finger_speed = FINGER_SPEED, starting_pos=FINGER_POS)
    total_cost = 0

    for _ in range(sample):
        typed = []
        text_type  = random.choice(["medium"])
        with open(f"sample_text\\{text_type}.txt", "r") as f:
            text = f.readlines()
        testing_text = text[random.randint(0, len(text)-1)]
        capslock = False

        
        while not(len(typed) >= len(testing_text)-1):
            try:
                cost, letter, fingers = autotyper.type(testing_text, typed, capslock)
            except Exception:
                print(testing_text[len(typed):], typed, letter)
                raise Exception
            if "caps lock" in letter:
                capslock = False if capslock == True else True
            for i in letter:
                if len(i) == 1:
                    typed.append(i)
                if i == "space":
                    typed.append(" ")
            total_cost += cost

    return total_cost/sample



def train():

    gens = Genetic(population_number=100, selection_method="tournament", selection_rate=0.9, mutation_rate=0.05,
            mutation_intensity=1, fitness_function=fit_keyboard, eltism=0.1)

    gens.simulate(generation=100, save=10, name="simulation2")


def main():
    print()
    train()
    


if __name__ == "__main__":
    main()