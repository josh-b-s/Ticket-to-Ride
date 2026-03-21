import random

def main():
    print("Number Guessing Game")
    number = random.randint(1, 10)

    while True:
        guess = input("Guess a number between 1 and 10: ")

        if not guess.isdigit():
            print("Please enter a valid number.")
            continue

        guess = int(guess)

        if guess < number:
            print("Too low!")
        elif guess > number:
            print("Too high!")
        else:
            print("Correct! You win!")
            break

if __name__ == "__main__":
    main()