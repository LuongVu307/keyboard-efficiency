import pygame
import os
import sys
import random
import csv
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

from autotype import Type10Finger


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
                ["caps lock"] + second + ["Enter"],
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

def create_frequency_map(layout, dist_layout, frequency_map, output_path):
    """
    Creates an image of a keyboard layout with rectangles colored based on key frequencies.

    Parameters:
    - layout: List of lists representing the keyboard layout.
    - dist_layout: List of lists representing the distance metrics for each key.
    - text: Sample text to calculate key frequencies.
    - output_image_path: Path where the output image will be saved.
    """
    

    # Image size parameters
    rect_width = 1
    rect_height = 1
    rows = len(layout)
    cols = max(len(row) for row in layout)

    # Normalize frequencies for color mapping
    flat_frequencies = [frequency_map.get(key, 0) for sublist in layout for key in sublist]
    max_freq = max(flat_frequencies, default=1)
    norm_freq = mcolors.Normalize(vmin=0, vmax=max_freq)
    cmap_freq = plt.get_cmap('RdYlGn_r')  # Red colormap for frequency

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(cols, rows))
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')

    # Draw rectangles and annotate with frequency
    for r, (row, dist_row) in enumerate(zip(layout, dist_layout)):
        row_width = len(row) * rect_width
        row_offset = (cols - row_width) / 2  # Center the row horizontally

        for c, (key, dist) in enumerate(zip(row, dist_row)):
            # Calculate the center position of the rectangle
            x = row_offset + c * rect_width + rect_width / 2
            y = (rows - r - 1) * rect_height + rect_height / 2
            
            # Get frequency and map to color
            freq = frequency_map.get(key, 0)
            freq_color = cmap_freq(norm_freq(freq))
            
            # Draw rectangle with color based on frequency
            rect = plt.Rectangle((row_offset + c * rect_width, (rows - r - 1) * rect_height),
                                 rect_width, rect_height,
                                 linewidth=1, edgecolor='black', facecolor=freq_color)
            ax.add_patch(rect)
            
            # Draw key text with frequency
            plt.text(x, y, f"{key}\n{round(freq/sum(frequency_map.values()), 3)}", ha='center', va='center', fontsize=8, color='black')

    # Remove axes
    ax.axis('off')

    # Save the image
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

def create_line_graph(x, y, output_path):
    """
    Draws a line graph of the provided x and y data and saves it as an image file.
    
    Parameters:
    - x: Data for the x-axis.
    - y: Data for the y-axis.
    - output_image_path: Path where the output image will be saved.
    """
    # Create the line plot
    plt.plot(x, y, linestyle='-', color='b', label='Line')
    
    # Add titles and labels
    plt.title('LDS of generations')
    plt.xlabel('Generation')
    plt.ylabel('Inverse LDS')
    
    # Save the plot to an image file
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()  # Close the figure to free up memory

class Genetic:
    def __init__(self, population_number, selection_method, selection_rate, mutation_rate, 
                 mutation_intensity, dominant):
        self.population = {}

        self.population_number = population_number
        self.selection = selection_method
        self.selection_rate = selection_rate
        self.mutation_rate = mutation_rate
        self.mutation_intensity = mutation_intensity
        self.dominant = dominant

        self.all_the_time_best = ["", 1e99]

        self.frequency = {}


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
        print(f"Dominant intensity: {dominant*100}%")
        print("-------------------------------------------------------------")
        print()
        

    def fit(self):
        # count = 0
        while len(self.population) < self.population_number:
            self.population[str(generate_keyboard())] = 1e10
        for individual in self.population:
            self.population[individual] = self.fitness_function(process_string(individual))[0]

        self.population = dict(sorted(self.population.items(), key=lambda x : x[1]))
        min_value = min(self.population.values())
        self.best_performance = {key : value for key, value in self.population.items() if value == min_value}

        if list(self.best_performance.values())[0] < self.all_the_time_best[1]:
            self.all_the_time_best = [list(self.best_performance.keys())[0], list(self.best_performance.values())[0]]

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
        new_population_length = round(len(self.population)*self.selection_rate)
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

    def available_key(self):
        keyboard_example = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
        ["Tab", "" ,"" ,"" ,"" ,"" ,"" ,"" , "" ,"" ,"" ,"" ,"", "\\|"],
        ["caps lock", "" ,"" ,"" ,"" ,"" ,"" , "" , "" ,"" ,"","", "Enter"],
        ["LShift",   "" ,"" ,"" ,"" ,"" ,"" ,"" , "","","", "RShift",]
        ]

        self.available_keys = []
        for i in range(1, len(keyboard_example)):
            for j in range(len(keyboard_example[i])):
                    if keyboard_example[i][j] != "\\|":
                        self.available_keys.append((i, j))

    def get_important_genes(self):
        text_file = "medium"
        gene_repetition = {}

        keyboard_example = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
        ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
        ["caps lock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"", "Enter"],
        ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?", "RShift",]
        ]    

        for row in keyboard_example:
            for key in row:
                if len(key) <= 2:
                    gene_repetition[key] = 0



        # with open(f"sample_text/{text_file}.txt", "r") as f:
        #     lines = f.readlines()
        #     for line in lines:
        #         for word in line:
        #             for key in gene_repetition:
        #                 if word.upper() in key:
        #                     gene_repetition[key] += 1 
        #                 else: 
        #                     gene_repetition[key] = 1

 
        # gene_repetition = self.frequency
                                              

        sum_repetition = sum(self.frequency.values())
        for key in self.frequency:
            self.frequency[key] /= sum_repetition

        self.gene_importance =  dict(sorted(self.frequency.items(), key = lambda x : x[1], reverse=True))
        
    def get_similarities(self, keyboard1, keyboard2):
        similar, counter = 0, 0
        for i in range(len(keyboard1)):
            for j in range(len(keyboard1[i])):
                counter += 1
                if keyboard1[i][j] == keyboard2[i][j]:
                    similar += 1

        return similar/counter

    def combine(self, keyboard1, keyboard2):
        keyboard1_point = 1/list(keyboard1.values())[0]
        keyboard2_point = 1/list(keyboard2.values())[0]
        

        keyboard1 = process_string(list(keyboard1.keys())[0])
        keyboard2 = process_string(list(keyboard2.keys())[0])

        # print(keyboard1, keyboard2)

        child = [['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '', '', '', '', '']]

        filled = []
        for row1, row2 in zip(enumerate(keyboard1), enumerate(keyboard2)):
            for key1, key2 in zip(enumerate(row1[1]), enumerate(row2[1])):
                if key1[1] not in self.gene_importance:
                    if key2[1] not in self.gene_importance:
                        weights = [0.5, 0.5]   
                    else:
                        weights = [0.05, 0.95]
                elif key2[1] not in self.gene_importance:
                    weights = [0.05, 0.95]
                else:
                    weights = [keyboard1_point*self.gene_importance[key1[1]], keyboard2_point*self.gene_importance[key2[1]]]
                    if self.dominant != 0:
                        if weights[0] > weights[1]:
                            weights[0] /= self.dominant
                            weights[1] *= self.dominant
                        else:
                            weights[0] *= self.dominant
                            weights[1] /= self.dominant
                selected_key = self.weighted_random_choice([key1[1], key2[1]], weights)
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

    def calculate_probability(self, distance):
        return 1/(1+distance)
    
    def weighted_random_choice(self, genes, probabilities):
        total = sum(probabilities)
        r = random.uniform(0, total)
        cumulative = 0
        for gene, prob in zip(genes, probabilities):
            cumulative += prob
            if r < cumulative:
                return gene

    def select_matching_pair(self, genes):
        matching_pair = []
        available_genes = genes.copy()

        while len(available_genes) > 1:
            gene1 = random.choice(available_genes)
            # print(gene1)
            available_genes.remove(gene1)

            distances = [abs(list(gene1.values())[0] - list(gene2.values())[0]) for gene2 in available_genes]
            probabilities = [self.calculate_probability(d) for d in distances]
            mate = self.weighted_random_choice(available_genes, probabilities)

            available_genes.remove(mate)
            
            matching_pair.append([gene1, mate])

        return matching_pair

    def regenerate(self):
        
        # print(self.new_generation)
        self.new_generation = [{k: v} for k, v in self.new_generation.items()]
        # random.shuffle(self.new_generation)
        # self.new_generation = [self.new_generation[i:i + 2] for i in range(0, len(self.new_generation), 2)]

        mating_pairs = self.select_matching_pair(self.new_generation)
        # print(len(mating_pairs), type(mating_pairs))
        # print(len(mating_pairs), len(mating_pairs[0]))
        self.new_generation = []

        for count, couple in enumerate(mating_pairs):
            child1 = self.combine(couple[0], couple[1])
            child2 = self.combine(couple[0], couple[1])
            self.new_generation.append([child1, child2])

        # for i in self.new_generation:
        #     print(type(i), type(i[0]), type(i[1]))
        self.new_generation = [item for temp in self.new_generation for item in temp]
        
    def mutate(self, keyboard):
        # print(type(keyboard))
        count = int(self.mutation_intensity*20)
        while count != 0:
            choice1, choice2 = random.choice(self.available_keys), random.choice(self.available_keys)
            i1, j1 = choice1[0], choice1[1]
            i2, j2 = choice2[0], choice2[1]

            # print(keyboard[i1][j1], keyboard[i2][j2])

            if not (len(keyboard[i1][j1]) > 2 or len(keyboard[i2][j2]) > 2 or
                    keyboard[i1][j1] == "\\|" or keyboard[i2][j2] == "\\|"):
                keyboard[i1][j1], keyboard[i2][j2] = keyboard[i2][j2], keyboard[i1][j1]
                count -= 1
        return keyboard
    
    def elite(self):
        self.population = dict(sorted(self.population.items(), key=lambda x : x[1]))
        # print(self.population.values())
        keep = list(self.population.keys())[:int(len(self.population)-len(self.new_generation))]

        # for i in keep:
        #     print(self.population[i])

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
                    ["caps lock", "A", "R", "S", "T", "D", "H", "N", "E", "I", "O", "'\"", "Enter"],
                    ["LShift", "Z", "X", "C", "V", "B", "K", "M", ",<", ".>", "/?", "RShift"]
                ]

        self.get_important_genes()
        self.available_key()

        self.frequency = {i : 0 for j in QWERTY for i in j}
        self.history =  []

        for _ in range(generation):

            QWERTY_score = self.fitness_function(QWERTY)
            DVORAK_score = self.fitness_function(DVORAK)
            COLEMAK_score = self.fitness_function(COLEMAK)


            print("Generation: ", _, " Population: ", len(self.population))
            print("-----------------------------------------------")

            # print("Calculating metrics for the generations ...")
            self.fit()
            # print("Selecting strong keyboards")
            self.select()
            # print("Regenerating new keyboards")
            self.regenerate()        

            # for i in self.new_generation:
            #     print(type(i))
            # sys.exit()

            for count, genes in enumerate(self.new_generation):
                if self.weighted_random_choice([0, 1], probabilities=[1-self.mutation_rate, self.mutation_rate]) == 1:
                    self.new_generation[count] = self.mutate(genes)
            self.elite()

            print(f"Generation {_}'s best performance keyboard has the average typing inverse LPS of {list(self.best_performance.values())[0]}")
            print(f"Generation {_}'s keyboard has the average typing inverse LPS of {sum(list(self.population.values()))/len(self.population)}")
            print(f"QWERTY has LPS of {QWERTY_score[1]} and inverse LPS of {QWERTY_score[0]}")
            print(f"DVORAK has LPS of {DVORAK_score[1]} and inverse LPS of {DVORAK_score[0]}")
            print(f"COLEMAK has LPS of {COLEMAK_score[1]} and inverse LPS of {COLEMAK_score[0]}")
            
            print("The keyboard layout is")
            best_keyboard = process_string(list(self.best_performance.keys())[0])

            self.history.append(min(self.population.values()))
            if _ == generation-1:
                save_keyboard = [process_string(i) for i in list(self.population.keys())[:save]]
                
                # print(save_keyboard)
                with open(f'save/{name}.txt', 'w') as file:
                    for line in save_keyboard:
                        file.write(str(line) + '\n')

                dist_layout = [[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,14],
                [0.8, 2, 3, 4, 5 ,6 ,7, 8, 9, 10, 11, 12, 13, 14.3],
                [0.9, 2.2 ,3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2,12.2,13.9],
                [1.1, 2.7,3.7,4.7,5.7,6.7,7.7,8.7,9.7,10.7,11.7,13.6]
                ]

                os.makedirs(f"evaluation/{name}", exist_ok=True)
                # print(self.frequency)

                # print(list(self.best_performance.keys())[0])


                create_frequency_map(QWERTY, dist_layout, self.frequency, output_path=f"evaluation/{name}/QWERTY_frequency_map.png")
                create_frequency_map(DVORAK, dist_layout, self.frequency, output_path=f"evaluation/{name}/DVORAK_frequency_map.png")
                create_frequency_map(COLEMAK, dist_layout, self.frequency, output_path=f"evaluation/{name}/COLEMAK_frequency_map.png")
                create_frequency_map(best_keyboard, dist_layout, self.frequency, output_path=f"evaluation/{name}/generated_frequency_map.png")

                create_line_graph(range(len(self.history)), self.history, output_path=f"evaluation/{name}/generated_history.png")

                # print(self.history)

                

            for row in best_keyboard:
                print(row)

            print()
            self.population = {str(i) : 1e10 for i in self.new_generation}

         

    def fitness_function(self, keyboard, sample=30):
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
        WPS = 0

        for _ in range(sample):
            typed = []
            type = random.choice(os.listdir("sample_text"))
            # type = "code"
            text = random.choice(os.listdir("sample_text/" + type))
            with open(f"sample_text\\{type}\\{text}", "r") as f:
                text = f.readlines()

            starting_line = random.randint(0, len(text)-1)
            testing_text = ""
            while True:
                if text[starting_line]:
                    testing_text += text[starting_line]

                starting_line += 1
                if len(testing_text) > 300 or starting_line >= len(text):
                    testing_text = testing_text.replace("\n", " ")
                    # print(testing_text)
                    break
                
            testing_text = testing_text.strip()
            length = len(testing_text)
            capslock = False
            total_cost = 0

            
            while not(len(typed) >= len(testing_text)-1):
                try:
                    cost, letter, fingers = autotyper.type(testing_text, typed, capslock)
                except Exception:
                    # print("CHECING", (testing_text[len(typed):]), ord(testing_text[len(typed)]), "2", typed, "3",  letter)
                    raise Exception
                for i in letter:
                    for j in self.frequency:
                        if len(j) <= 2:
                            if i.lower() in j.lower():
                                self.frequency[j] += 1
                        else:
                            if i.lower() == j.lower():
                                self.frequency[j] += 1


                if "caps lock" in letter:
                    capslock = False if capslock == True else True
                for i in letter:
                    if len(i) == 1:
                        typed.append(i)
                    if i == "space":
                        typed.append(" ")
                total_cost += cost
            # print(total_cost)
            if total_cost == 0:
                continue
            WPS += length/total_cost
            # print(length/total_cost)

        return 100/(WPS/sample), WPS/sample

    def evaluate(self, keyboard, name):
        FINGER_POS = {"1" : (2, 1), "2" : (2, 2), "3" : (2, 3), "4" : (2, 4), "5" : (2, 7), "6" : (2, 8), "7" : (2, 9), "8" : (2, 10)}
        FINGER_SPEED = {"1" : 20, "2" : 30, "3" : 40, "4" : 50, "5" : 50, "6" : 40, "7" : 30, "8" : 20}
        FINGER_COLOR = {"0": pygame.Color("Gray"), "1" : pygame.Color("Pink"), "2" : pygame.Color("Red"), "3" : pygame.Color("Yellow"), "4" : pygame.Color("Green"), "5" : pygame.Color("Blue"), "6" : pygame.Color("Purple"), "7" : pygame.Color("Brown"), "8" : pygame.Color("Light blue")}

        dist_layout = [[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,14],
                        [0.8, 2, 3, 4, 5 ,6 ,7, 8, 9, 10, 11, 12, 13, 14.3],
                        [0.9, 2.2 ,3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2,12.2,13.9],
                        [1.1, 2.7,3.7,4.7,5.7,6.7,7.7,8.7,9.7,10.7,11.7,13.6]
                        ]
        
        autotyper = Type10Finger(keyboard=keyboard, dist_layout =dist_layout, finger_speed = FINGER_SPEED, starting_pos=FINGER_POS)
        data = []

        for file in (os.listdir("sample_text/evaluation")):
            print(f"    -{file}")
            typed = []
            # type = "code"
            # text = random.choice(os.listdir("sample_text/" + type))
            with open(f"sample_text\\evaluation\\{file}", "r") as f:
                text = f.readlines()
            testing_text = "".join(text)
            testing_text = testing_text.replace("\n", " ")
            testing_text = testing_text.strip()
            # print(testing_text)
            length = len(testing_text)
            length_word = len(testing_text.split())
            capslock = False
            total_cost = 0

            
            while not(len(typed) >= len(testing_text)-1):
                # try:
                # print(testing_text,"\n\n", typed)
                cost, letter, fingers = autotyper.type(testing_text, typed, capslock)
                # except Exception:
                #     # print("CHECING", (testing_text[len(typed):]), ord(testing_text[len(typed)]), "2", typed, "3",  letter)
                #     raise Exception
                for i in letter:
                    for j in self.frequency:
                        if len(j) <= 2:
                            if i.lower() in j.lower():
                                self.frequency[j] += 1
                        else:
                            if i.lower() == j.lower():
                                self.frequency[j] += 1


                if "caps lock" in letter:
                    capslock = False if capslock == True else True
                for i in letter:
                    if len(i) == 1:
                        typed.append(i)
                    if i == "space":
                        typed.append(" ")
                total_cost += cost
            # print(total_cost)
            if total_cost == 0:
                continue
            LPS = length/total_cost
            WPM = length_word/total_cost

            data.append([name, length, length_word, total_cost, WPM, LPS, file])
        

            # print(length/total_cost)
        return data



# def check_balance(times, repeat=30):
#     QWERTY = [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
#         ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
#         ["caps lock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"", "Enter"],
#         ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?", "RShift",]
#         ]

#     sample = []
#     for _ in range(times):
#         sample.append(fit_keyboard(QWERTY, sample=repeat)[0])

#     return sample


def train():
    # print(check_balance(times=30, repeat=30))
    gens = Genetic(population_number=10, selection_method="rank", selection_rate=0.8, mutation_rate=0.1,
            mutation_intensity=0.3, dominant=0.7)

    gens.simulate(generation=100, save=10, name="simulation1")

def evaluate():
    gens = Genetic(population_number=100, selection_method="rank", selection_rate=0.8, mutation_rate=0.1,
            mutation_intensity=0.3, dominant=0.7)

    keyboards = {
    "simulation1" : [['`~', '1!', '2@', '3#', '4$', '5%', '6^', '7&', '8*', '9(', '0)', '-_', '=+', 'backspace'], ['Tab', '\'"', 'W', 'F', 'U', 'M', '.>', 'C', 'I', 'Q', 'R', '/?', '[{', '\\|'], ['caps lock', ',<', 'T', 'E', 'D', 'O', 'A', 'S', 'P', 'N', 'B', ']}', 'Enter'], ['LShift', ';:', 'X', 'V', 'G', 'H', 'L', 'Y', 'J', 'Z', 'K', 'RShift']],
    "simulation2" : [['`~', '1!', '2@', '3#', '4$', '5%', '6^', '7&', '8*', '9(', '0)', '-_', '=+', 'backspace'], ['Tab', 'Z', ';:', 'N', ']}', '[{', 'L', 'I', '\'"', 'H', 'E', '.>', 'F', '\\|'], ['caps lock', ',<', 'T', 'S', 'R', 'X', 'V', 'P', 'C', 'J', 'U', 'K', 'Enter'], ['LShift', 'Y', 'A', 'W', 'Q', '/?', 'G', 'O', 'D', 'B', 'M', 'RShift']],
    "simulation3" : [['`~', '1!', '2@', '3#', '4$', '5%', '6^', '7&', '8*', '9(', '0)', '-_', '=+', 'backspace'], ['Tab', 'X', 'K', 'H', 'D', 'C', 'B', 'L', 'I', 'T', 'J', ';:', ']}', '\\|'], ['caps lock', '[{', 'E', 'S', 'O', 'R', 'P', 'A', 'N', 'Y', '\'"', 'U', 'Enter'], ['LShift', 'Q', 'M', ',<', 'W', '/?', '.>', 'F', 'Z', 'G', 'V', 'RShift']],
    "QWERTY" : [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","-_" ,"=+", "backspace"],
            ["Tab", "Q" ,"W" ,"E" ,"R" ,"T" ,"Y" ,"U" ,  "I" ,"O" ,"P" ,"[{" ,"]}", "\\|"],
            ["caps lock", "A" ,"S" ,"D" ,"F" ,"G" ,"H" , "J" , "K" ,"L" ,";:","'\"", "Enter"],
            ["LShift",   "Z" ,"X" ,"C" ,"V" ,"B" ,"N" ,"M" , ",<",".>","/?", "RShift",]
            ],

    "DVORAK" : [["`~", "1!","2@","3#","4$","5%","6^", "7&","8*","9(","0)","[{" ,"]}", "backspace"],
            ["Tab", "'\"" ,",<" ,".>" ,"P" ,"Y" ,"F" ,"G" , "C" ,"R" ,"L" ,"/?" ,"=+", "\\|"],
            ["caps lock", "A" ,"O" ,"E" ,"U" ,"I" ,"D" , "H" , "T" ,"N" ,"S","-_", "Enter"],
            ["LShift", ";:", "Q" ,"J" ,"K" ,"X" ,"B" ,"M" ,"W" , "V", "Z", "RShift",]
            ],

    "COLEMAK" : [["`~", "1!", "2@", "3#", "4$", "5%", "6^", "7&", "8*", "9(", "0)", "-_", "=+", "backspace"],
                ["Tab", "Q", "W", "F", "P", "G", "J", "L", "U", "Y", ";:", "[{", "]}", "\\|"],
                ["caps lock", "A", "R", "S", "T", "D", "H", "N", "E", "I", "O", "'\"", "Enter"],
                ["LShift", "Z", "X", "C", "V", "B", "K", "M", ",<", ".>", "/?", "RShift"]
            ]
    }
    data = [['keyboard','letters','words','time','wpm','lps','text']]
    for keyboard in keyboards:
        # print(list(gens.evaluate(keyboard=keyboards[keyboard], name=keyboard)))
        print(keyboard)
        data += list(gens.evaluate(keyboard=keyboards[keyboard], name=keyboard))

        
        # print(data)
    with open("evaluation.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

        



def main():
    args = sys.argv
    print()
    if len(args) > 1:
        if args[1] == "--train":
            train()
        elif args[1] == "--eval":
            evaluate()
    else:
        raise Exception("Invalid arguments")
    
    # gens = Genetic(population_number=100, selection_method="tournament", selection_rate=0.9, mutation_rate=0.05,
    #         mutation_intensity=1, fitness_function=fit_keyboard, eltism=0.1)
    
    # print(gens.get_important_genes())

    


if __name__ == "__main__":
    main()