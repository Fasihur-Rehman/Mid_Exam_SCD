# Focus Session Manager

This is a simple Python program for people who want to use their devices more mindfully.

The program allows you to:

- Start a focus session with a session name.
- Finish the session when you are done.
- View your completed focus sessions.
- View a productivity summary with streaks and achievement badges.
- Set a daily focus-time limit.
- Receive random focus tips.
- Receive a random offline activity suggestion.
- Get a break suggestion after finishing a session.
- Save session data in an XML file.
- Load saved sessions when the program starts again.

The program uses functions, lists, dictionaries, input validation, regular expressions, random selection, date calculations, and XML. It does not use classes or object-oriented programming.
## Requirements

- Python 3.x
- No additional packages are required.

Python includes the modules used by this project, such as `re`, `random`, `datetime`, `pathlib`, and `xml.etree.ElementTree`.

## Files

```text
FasihUrRehman_YousafUrRehman.py   Main program
focus_sessions.xml                Saved session data
README.md                         This instruction file
```

The XML file is created automatically beside the Python file. It stores the daily limit and completed sessions.

## How to run

1. Open a terminal or PowerShell window.
2. Move to the project folder.
3. Run the Python file.

For example, on Windows:

```powershell
cd "C:\Users\Fasih\Desktop\Fasih_Lab_Exam"
python FasihUrRehman_YousafUrRehman.py
```

If the `python` command does not work, use the full Python path:

```powershell
& "C:/Program Files/Python314/python.exe" "FasihUrRehman_YousafUrRehman.py"
```

## Using the menu

When the program starts, it displays this menu:

```text
1. Start focus session
2. Finish current session
3. View completed sessions
4. Show productivity summary
5. Show a focus tip
6. Suggest offline activity
7. Export XML report
8. Import XML report
9. Exit
```

When a session is active, option 2, **Finish current session**, is shown in green so it is easy to find.

### 1. Start focus session

The program asks for:

- The session name.
- The planned session duration.
- The daily focus-time limit.

The session name must start with a letter and can contain letters, numbers, spaces, `_`, and `-`.

The planned duration must be between 1 and 180 minutes. The daily limit must be between 1 and 1440 minutes.

After starting, the program returns to the menu. Keep using your device or work until you are ready to finish the session.

### 2. Finish current session

Choose this option when you are finished. The program calculates how long the session was active, adds it to the history, and automatically saves the data in `focus_sessions.xml`.

Always finish the active session before choosing Exit. An active session is not saved as a completed session until it is finished.

### 3. View completed sessions

This option displays each completed session, including:

- Session name.
- Planned duration.
- Actual time used.
- Start date and time.
- Total focus time.
- Daily limit.

### 4. Show productivity summary

This option shows the total number of sessions, total focus time, average session length, longest session, and current focus streak.

It also gives achievement badges such as `First Step`, `One Hour Focus`, `Deep Work`, `Three-Day Streak`, and `Focus Champion`.

### 5. Show a focus tip

This option randomly displays a simple focus tip, such as putting your phone on silent or writing down distracting thoughts.

### 6. Suggest offline activity

This option randomly suggests an activity such as taking a walk, reading, stretching, or talking with a family member.

After a session is finished, the program also gives a break suggestion. Longer sessions receive longer break suggestions.

### 7. Export XML report

This option asks for an XML filename and saves the current report to that file. For example:

```text
weekly_report.xml
```

### 8. Import XML report

This option loads a report from an XML file. The imported data also becomes the new automatically saved data.

### 9. Exit

This closes the program. The program saves the current completed session history before exiting.

## Example workflow

```text
Enter your choice (1-9): 1
Enter the session name: Study Session
Enter planned duration (1-180 minutes): 25
Enter daily focus limit (1-1440 minutes): 120
Focus session started for 'Study Session'.

Enter your choice (1-9): 2
Session finished: Study Session | used 0.2 minutes.
Total focus time: 0.2 / 120 minutes
Break suggestion: Take a 5-minute break, drink water, and rest your eyes.

Enter your choice (1-9): 3
Completed sessions:
1. Study Session | planned: 25 min | used: 0.2 min
```

The actual time will be different because it depends on how long the session remains active.

## How XML storage works

The program uses `focus_sessions.xml` as a small data file. It stores information such as:

- The daily limit.
- The session name.
- Planned minutes.
- Start time.
- End time.
- Actual elapsed seconds.

When the program starts, it reads this file. When a session is finished, it writes the updated information back to the file.
