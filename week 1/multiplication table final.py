print ("multiplication table generator")
num = int(input("Enter a number for the table: "))

print(f"Multiplication Table for {num}:")
for i in range(1, 11):
    result = num * i
    print(f"{num} x {i} = {result}")
print ("thank you ")
