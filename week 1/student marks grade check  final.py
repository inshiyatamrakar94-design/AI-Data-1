while True:
    score = float(input("Enter marks (0-100): "))

    if 0 <= score <= 100:
        break  # Success! Exit the loop.
    else:
        print("Invalid input. Try again.")

# The program only reaches this part once the loop breaks
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "Fail"

print(f"Final Score: {score}")
print(f"Final Grade: {grade}")
