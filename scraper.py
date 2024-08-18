import os
import sys
import requests
from bs4 import BeautifulSoup

def scraper1():
    url = 'https://randomword.com/paragraph'
    response = requests.get(url)
    webpage = response.content
    soup = BeautifulSoup(webpage, 'html.parser')

    div_id = 'random_word_definition'
    specific_div = soup.find('div', id=div_id)

    if specific_div:
        result = specific_div.text
        with open("sample_text\\all_text.txt", "a") as file:
            file.write(result + "\n")
    else:
        print(f'Div with id {div_id} not found')
        raise Exception

def check_valid(string):
    valid_char = "abcdefghijklmnopqrstuv"
    valid_char += valid_char.upper()
    valid_char += "1234567890-=!@#$%^&*()_+[]{};':\",./<>?"
    result = ""
    for char in string:
        if char not in valid_char:
            result += char
    return string

def sorter():
    with open("sample_text\\all_text.txt", "r") as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines]
    for line in lines:
        line = check_valid(line)
        if len(line) < 280:
            file_name = "short"
        elif len(line) < 350:
            file_name = "medium"
        elif len(line) < 500:
            file_name = "long"

        with open(f"sample_text\\{file_name}.txt", "r") as file:
            already_in = False
            lines = file.readlines()
            for line_check in lines:
                if line_check.strip() == line:
                    already_in = True
                
            if not already_in:
                with open(f"sample_text\\{file_name}.txt", "a") as file:
                    file.write(line + "\n")
        
    
    with open('sample_text\\all_text.txt', 'w') as file:
        file.write("")





def main():
    N = int(input("Number of paragraphs: "))
    for _ in range(N):
        scraper1()
        print(_+1 , end=", ")
    sorter()



if __name__ == "__main__":
    main()