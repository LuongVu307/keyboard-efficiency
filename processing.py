import os
import sys
import shutil
import requests
from bs4 import BeautifulSoup
import PyPDF2

def scraper1():
    url = 'https://randomtextgenerator.com/'
    response = requests.get(url)
    webpage = response.content
    soup = BeautifulSoup(webpage, 'html.parser')

    div_id = 'randomtext_box'
    specific_div = soup.find('div', id=div_id)

    if specific_div:
        result = specific_div.text
        cleaned_content = ''.join(char for char in result if ord(char) < 128)

        with open("sample_text\\dummy\\simple.txt", "a") as file:
            file.write(cleaned_content.strip() + "\n")

        with open("sample_text\\dummy\\simple.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()

        cleaned_lines = [line for line in lines if line.strip()]

        with open("sample_text\\dummy\\simple.txt", "w", encoding="utf-8") as file:
            file.writelines(cleaned_lines)



            
    else:
        print(f'Div with id {div_id} not found')
        raise Exception
    
def pdf_to_text(pdf_file_path, output_file_path=None):
    """
    Extracts text from a PDF file and returns it as a string. 
    Optionally writes the text to a .txt file.

    Args:
        pdf_file_path (str): Path to the input PDF file.
        output_file_path (str, optional): Path to the output .txt file. If None, the text is not written to a file.

    Returns:
        str: The extracted text from the PDF.
    """
    # Open the PDF file in binary mode
    with open("sample_text/articles/" + pdf_file_path, 'rb') as pdf_file:
        # Initialize PDF reader object
        try:
            reader = PyPDF2.PdfReader(pdf_file)

            # Create an empty string to store the extracted text
            text = ""

            # Loop through all the pages and extract text
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()

            # If an output file path is provided, write the text to the file
            if output_file_path:
                with open("sample_text/articles/" + output_file_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(text)
            os.remove("sample_text/sample_text/articles/" + pdf_file_path)
                # print(f"PDF text extraction complete! Saved to {output_file_path}.")
        except Exception:
            pass
        validate("articles/" + output_file_path[:-4])

        
def validate(input_path):
    with open(f"sample_text/{input_path}.txt", "r", encoding="utf-8", errors="ignore") as file:
        content = file.read()

    cleaned_content = ''.join(char for char in content if ord(char) < 128)


    # Write the cleaned content back to the file
    with open(f"sample_text/{input_path}.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_content)


    with open(f"sample_text/{input_path}.txt", "r", encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()

    stripped_lines = [line.strip() for line in lines]


    # Write the cleaned content back to the file
    with open(f"sample_text/{input_path}.txt", "w", encoding="utf-8") as file:
        file.write('\n'.join(stripped_lines))


    

def process_book(input_path):
    validate("evaluation/"+input_path)
    with open(f"sample_text/evaluation/{input_path}.txt", "r+") as file:
        content = file.read()
        
        content = content.replace("    ", "")
        content = content.replace("\n\n", "\n")


        file.seek(0)
        file.write(content)

def process_and_delete_repo(source_dir, dest_file):
    with open(dest_file, 'w', encoding='utf-8') as output_file:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.cpp'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as src_file:
                            content = src_file.read()
                            output_file.write(content + "\n\n")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

    try:
        shutil.rmtree(source_dir)
        print(f"Deleted repository at {source_dir}")
    except Exception as e:
        print(f"Error deleting {source_dir}: {e}")



def main():
    # for i in os.listdir("sample_text/code"):
    #     validate(f"code/{i[:-4]}")
    book_name = input("Book Processing Name: ")
    if book_name:
        if book_name == "all":
            for name in os.listdir(f"sample_text/evaluation"):
                process_book(name[:-4])
        else:
            process_book(book_name)

    N = input("Number of paragraphs: ")
    if N:
        N = int(N)
        for _ in range(N):
            scraper1()
            print(_+1 , end=", ")
        # sorter()

    article = input("Input Name of article: ")
    if article:
        if article == "all":
            for name in os.listdir(f"sample_text/articles"):
                pdf_to_text(name, name[:-4]+".txt")
        else:
            pdf_to_text(name, name[:-4]+".txt")


    for name in os.listdir(f"sample_text/code"):
        validate("code/" + name[:-4])




if __name__ == "__main__":
    main()