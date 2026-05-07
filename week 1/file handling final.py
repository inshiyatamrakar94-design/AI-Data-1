import os

print(f"Current Folder Python is looking in: {os.getcwd()}")
print(f"Files I can see here: {os.listdir()}")

def start_word_counter():
    # 1. Ask for the file name
    target_file = input("Please enter the filename to scan: ")

    # 2. Start the safety block
    try:
        # 3. Open the file ('r' means read mode)
        with open(target_file, 'r') as file:
            # 4. Read the whole file into a variable
            text_data = file.read()
            
            # 5. Split text into a list by looking for spaces
            word_list = text_data.split()
            
            # 6. Count the items in the list
            total_words = len(word_list)
            
            print(f"Success! Found {total_words} words in '{target_file}'.")

    # 7. If the file isn't found, run this instead of crashing
    except FileNotFoundError:
        print(f"Error: The file '{target_file}' was not found. Please check the spelling.")
    
    # 8. Catch any other random errors (like permission issues)
    except Exception as e:
        print(f"Something went wrong: {e}")

# Run the program
start_word_counter()
