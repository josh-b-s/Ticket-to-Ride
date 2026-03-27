import random


def main():
    print("Welcome to Rock-Paper-Scissors!")
    print("Enter your choice: rock, paper, or scissors.")

    choices = ["rock", "paper", "scissors"]

    while True:
        player = input("Your choice: ").strip().lower()
        if player not in choices:
            print("Invalid choice. Please choose rock, paper, or scissors.")
            continue

        computer = random.choice(choices)
        print(f"Computer chose: {computer}")

        if player == computer:
            print("It's a tie!")
        elif (player == "rock" and computer == "scissors") or \
                (player == "scissors" and computer == "paper") or \
                (player == "paper" and computer == "rock"):
            print("You win!")
        else:
            print("You lose!")

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()