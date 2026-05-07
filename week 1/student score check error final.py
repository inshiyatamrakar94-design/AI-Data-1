score = float(input("Enter the student's marks: "))

# Check if the score is physically possible
if score < 0 or score > 100:
    print("Error: Please enter a score between 0 and 100.")
else:
    # This only runs if the score is valid
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

    print(f"Score: {score}")
    print(f"Grade: {grade}")
