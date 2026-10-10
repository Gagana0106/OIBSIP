# OIBSIP – Task 3: Advanced Password Generator

## Project Overview
The Advanced Password Generator is a Python application that generates secure and random passwords based on the user's preferences. It provides a graphical user interface (GUI) using Tkinter and uses Python's `secrets` module for secure password generation.

## Features
- Generate passwords with a customizable length from 8 to 20 characters.
- Select uppercase letters, lowercase letters, digits, and symbols.
- Exclude ambiguous characters such as `0`, `O`, `I`, `l`, and `1`.
- Display password strength as Weak, Medium, or Strong.
- Copy generated passwords to the clipboard.
- View the last five generated passwords during the current session.
- Validate user selections before generating a password.

## Technologies Used
- Python
- Tkinter
- Secrets
- String
- Pyperclip

## Installation
Install the required library by running:

```bash
python -m pip install pyperclip
```

## How to Run
1. Download or clone this repository.
2. Open the project folder.
3. Open the Python file in IDLE or another Python editor.
4. Run the program.
5. Select your preferred character types and password length.
6. Click the generate button to create a password.
7. Use the copy option to copy the password to the clipboard.

## Security
The application uses Python's `secrets` module to generate passwords securely. Users can customize the character types included in the generated password.

**Note:** Password history is stored only during the current application session and is not saved permanently.

## Learning Outcome
This project demonstrates the use of Python GUI development, secure random password generation, input validation, clipboard functionality, and password-strength assessment.

## Internship
**Organization:** Oasis Infobyte  
**Internship Track:** Python Programming  
**Task:** Task 3 – Advanced Password Generator
