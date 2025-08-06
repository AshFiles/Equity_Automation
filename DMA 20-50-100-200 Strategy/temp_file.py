def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    print("Age is:", age)

check_age(25)
check_age(-3)
