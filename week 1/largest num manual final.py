def find_largest (numbers):
    if not numbers:
        return None
    
    largest = numbers[0]
    for num in numbers:
    
        if num > largest:
            largest = num
    return largest

# taking input from the user
user_input =input ("enter numbers seperated by spaces:")
# converting the input string into a list of integers
num_list = [float (x) for x in user_input.split()]
# finding the largest number
result =find_largest (num_list)
# printing the result
if result is not None:
    print(f"The largest number is: {result}")
else:
    print("No numbers were entered.")