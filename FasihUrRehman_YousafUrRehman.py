import random
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


MIN_SESSION_MINUTES = 1
MAX_SESSION_MINUTES = 180
DEFAULT_DAILY_LIMIT = 120
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATA_FILE = Path(__file__).with_name("focus_sessions.xml")
GREEN_TEXT = "\033[92m"
RESET_TEXT = "\033[0m"

SESSION_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]{1,39}$")
DURATION_PATTERN = re.compile(r"^\d{1,3}$")

OFFLINE_ACTIVITIES = [
    "Take a short walk",
    "Read a few pages of a book",
    "Drink water and stretch",
    "Write a quick journal entry",
    "Talk with a family member",
]

FOCUS_TIPS = [
    "Put your phone on silent while you work.",
    "Choose one small task and finish it before switching tasks.",
    "Keep water nearby so you do not need unnecessary screen breaks.",
    "If you feel distracted, take three slow breaths and return to your task.",
    "Write down distracting thoughts and handle them after the session.",
]

sessions = []
current_session = None
daily_limit_minutes = DEFAULT_DAILY_LIMIT


def is_valid_session_name(session_name):
    """Return True when the session name has a safe, readable format."""
    return bool(SESSION_NAME_PATTERN.fullmatch(session_name.strip()))


def is_valid_duration(duration_text):
    """Return True when the duration is a whole number of minutes."""
    if not DURATION_PATTERN.fullmatch(duration_text.strip()):
        return False
    duration = int(duration_text)
    return MIN_SESSION_MINUTES <= duration <= MAX_SESSION_MINUTES


def format_time(seconds):
    """Convert seconds into a simple minutes and seconds display."""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"


def create_session(session_name, planned_minutes):
    """Create one session dictionary."""
    return {
        "session_name": session_name,
        "planned_minutes": planned_minutes,
        "started_at": datetime.now(),
        "ended_at": None,
        "elapsed_seconds": 0,
    }


def start_session(session_name, planned_minutes):
    """Start a session if another session is not already active."""
    global current_session
    if current_session is not None:
        return False
    current_session = create_session(session_name, planned_minutes)
    return True


def stop_session(session_elapsed_seconds):
    """Finish the current session and add it to the session list."""
    global current_session
    if current_session is None:
        return None

    current_session["elapsed_seconds"] = session_elapsed_seconds
    current_session["ended_at"] = datetime.now()
    finished_session = current_session
    sessions.append(finished_session)
    current_session = None
    return finished_session


def get_total_minutes():
    """Return the total completed focus time in minutes."""
    total_seconds = sum(session["elapsed_seconds"] for session in sessions)
    return total_seconds / 60


def get_daily_limit(limit_text):
    """Validate and return the daily limit entered by the user."""
    limit_text = limit_text.strip()
    if not DURATION_PATTERN.fullmatch(limit_text):
        raise ValueError("Daily limit must be a whole number of minutes.")

    limit = int(limit_text)
    if limit < MIN_SESSION_MINUTES or limit > 1440:
        raise ValueError("Daily limit must be between 1 and 1440 minutes.")
    return limit


def export_xml(filename):
    """Save the daily limit and session history in an XML file."""
    root = ET.Element("focus_report")
    root.set("created_at", datetime.now().strftime(DATE_FORMAT))

    settings = ET.SubElement(root, "settings")
    ET.SubElement(settings, "daily_limit_minutes").text = str(daily_limit_minutes)

    sessions_element = ET.SubElement(root, "sessions")
    for session in sessions:
        session_element = ET.SubElement(sessions_element, "session")
        ET.SubElement(session_element, "session_name").text = session["session_name"]
        ET.SubElement(session_element, "planned_minutes").text = str(
            session["planned_minutes"]
        )
        ET.SubElement(session_element, "started_at").text = session[
            "started_at"
        ].strftime(DATE_FORMAT)
        ET.SubElement(session_element, "ended_at").text = session["ended_at"].strftime(
            DATE_FORMAT
        )
        ET.SubElement(session_element, "elapsed_seconds").text = str(
            session["elapsed_seconds"]
        )

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(filename, encoding="utf-8", xml_declaration=True)


def import_xml(filename):
    """Read an XML report and return its daily limit and session list."""
    tree = ET.parse(filename)
    root = tree.getroot()
    settings = root.find("settings")
    sessions_element = root.find("sessions")

    if settings is None or sessions_element is None:
        raise ValueError("The XML file does not contain a valid focus report.")

    limit_text = settings.findtext("daily_limit_minutes")
    if limit_text is None or not limit_text.isdigit():
        raise ValueError("The XML file contains an invalid daily limit.")

    loaded_sessions = []
    for session_element in sessions_element.findall("session"):
        # The fallback supports reports created by the older version.
        session_name = session_element.findtext("session_name")
        if session_name is None:
            session_name = session_element.findtext("app_name")
        planned_text = session_element.findtext("planned_minutes")
        started_text = session_element.findtext("started_at")
        ended_text = session_element.findtext("ended_at")
        elapsed_text = session_element.findtext("elapsed_seconds")

        values = [session_name, planned_text, started_text, ended_text, elapsed_text]
        if not all(values):
            raise ValueError("A session in the XML file is incomplete.")

        session = create_session(session_name, int(planned_text))
        session["started_at"] = datetime.strptime(started_text, DATE_FORMAT)
        session["ended_at"] = datetime.strptime(ended_text, DATE_FORMAT)
        session["elapsed_seconds"] = int(elapsed_text)
        loaded_sessions.append(session)

    return int(limit_text), loaded_sessions


def save_saved_data():
    """Automatically save the current sessions beside this Python file."""
    try:
        export_xml(DATA_FILE)
        return True
    except OSError:
        return False


def load_saved_data():
    """Load the automatic XML file when it exists."""
    global sessions, daily_limit_minutes

    if not DATA_FILE.exists():
        return True

    try:
        daily_limit_minutes, sessions = import_xml(DATA_FILE)
        return True
    except (OSError, ET.ParseError, ValueError):
        sessions = []
        daily_limit_minutes = DEFAULT_DAILY_LIMIT
        return False


def get_text_input(prompt):
    """Keep asking until the user enters non-empty text."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def get_integer_input(prompt, minimum, maximum):
    """Read and validate a whole number within a given range."""
    while True:
        value = input(prompt).strip()
        if not DURATION_PATTERN.fullmatch(value):
            print("Please enter a whole number.")
            continue

        number = int(value)
        if minimum <= number <= maximum:
            return number
        print(f"Please enter a number from {minimum} to {maximum}.")


def start_cli_session():
    """Read session details and start a focus session."""
    global daily_limit_minutes

    if current_session is not None:
        print("A session is already active. Finish it before starting another.")
        return

    session_name = get_text_input("Enter the session name: ")
    if not is_valid_session_name(session_name):
        print("Use a session name with 2-40 characters starting with a letter.")
        return

    duration = get_integer_input(
        f"Enter planned duration ({MIN_SESSION_MINUTES}-{MAX_SESSION_MINUTES} minutes): ",
        MIN_SESSION_MINUTES,
        MAX_SESSION_MINUTES,
    )
    daily_limit = get_integer_input(
        "Enter daily focus limit (1-1440 minutes): ",
        MIN_SESSION_MINUTES,
        1440,
    )
    daily_limit_minutes = daily_limit

    start_session(session_name, duration)
    print(f"Focus session started for '{session_name}'.")
    print("Choose 'Finish current session' from the menu when you are done.")


def stop_cli_session():
    """Finish the active session and save it automatically."""
    if current_session is None:
        print("There is no active session.")
        return

    elapsed = int((datetime.now() - current_session["started_at"]).total_seconds())
    finished_session = stop_session(max(elapsed, 0))
    save_saved_data()
    used_minutes = finished_session["elapsed_seconds"] / 60
    print(
        f"Session finished: {finished_session['session_name']} | "
        f"used {used_minutes:.1f} minutes."
    )
    print(
        f"Total focus time: {get_total_minutes():.1f} / "
        f"{daily_limit_minutes} minutes"
    )
    print("Break suggestion:", get_break_suggestion(used_minutes))


def view_sessions():
    """Print all completed focus sessions."""
    if not sessions:
        print("No completed sessions yet.")
        return

    print("\nCompleted sessions:")
    for number, session in enumerate(sessions, start=1):
        used_minutes = session["elapsed_seconds"] / 60
        started = session["started_at"].strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{number}. {session['session_name']} | "
            f"planned: {session['planned_minutes']} min | "
            f"used: {used_minutes:.1f} min | started: {started}"
        )
    print(f"Total focus time: {get_total_minutes():.1f} minutes")
    print(f"Daily limit: {daily_limit_minutes} minutes")


def suggest_offline_activity():
    """Randomly print an offline activity suggestion."""
    print("Offline activity suggestion:", random.choice(OFFLINE_ACTIVITIES))


def get_focus_streak():
    """Return the number of consecutive days with completed sessions."""
    if not sessions:
        return 0

    session_dates = {session["started_at"].date() for session in sessions}
    check_date = datetime.now().date()
    if check_date not in session_dates:
        check_date = check_date - timedelta(days=1)

    streak = 0
    while check_date in session_dates:
        streak += 1
        check_date = check_date - timedelta(days=1)
    return streak


def show_productivity_summary():
    """Display totals, averages, streaks, and achievement badges."""
    if not sessions:
        print("Complete a session first to see a productivity summary.")
        return

    total_minutes = get_total_minutes()
    average_minutes = total_minutes / len(sessions)
    longest_session = max(sessions, key=lambda session: session["elapsed_seconds"])
    streak = get_focus_streak()

    print("\n===== Productivity Summary =====")
    print("Completed sessions:", len(sessions))
    print(f"Total focus time: {total_minutes:.1f} minutes")
    print(f"Average session: {average_minutes:.1f} minutes")
    print(
        "Longest session: "
        f"{longest_session['session_name']} "
        f"({longest_session['elapsed_seconds'] / 60:.1f} minutes)"
    )
    print("Current focus streak:", streak, "day(s)")

    badges = []
    if len(sessions) >= 1:
        badges.append("First Step")
    if total_minutes >= 60:
        badges.append("One Hour Focus")
    if any(session["planned_minutes"] >= 60 for session in sessions):
        badges.append("Deep Work")
    if streak >= 3:
        badges.append("Three-Day Streak")
    if total_minutes >= 300:
        badges.append("Focus Champion")

    print("Badges:", ", ".join(badges))
    print("================================")


def show_focus_tip():
    """Print a random tip for staying focused."""
    print("Focus tip:", random.choice(FOCUS_TIPS))


def get_break_suggestion(minutes):
    """Return a break suggestion based on the session length."""
    if minutes >= 60:
        return "Take a 15-minute offline break and stretch your body."
    if minutes >= 25:
        return "Take a 5-minute break, drink water, and rest your eyes."
    return "Stand up, breathe slowly, and take a short movement break."


def export_cli_report():
    """Export the current report to a filename entered by the user."""
    filename = get_text_input("Enter the XML filename: ")
    try:
        export_xml(filename)
        print("Report exported successfully.")
    except OSError as error:
        print(f"Could not export the report: {error}")


def import_cli_report():
    """Import a report and save it as the automatic report."""
    global daily_limit_minutes, sessions

    filename = get_text_input("Enter the XML filename to import: ")
    try:
        daily_limit_minutes, sessions = import_xml(filename)
        save_saved_data()
        print("Report imported successfully.")
    except (OSError, ET.ParseError, ValueError) as error:
        print(f"Could not import the report: {error}")


def print_menu():
    """Display the main menu options."""
    finish_option = "2. Finish current session"
    if current_session is not None:
        finish_option = f"{GREEN_TEXT}{finish_option}{RESET_TEXT}"

    print("\n===== Focus Session Manager =====")
    print("1. Start focus session")
    print(finish_option)
    print("3. View completed sessions")
    print("4. Show productivity summary")
    print("5. Show a focus tip")
    print("6. Suggest offline activity")
    print("7. Export XML report")
    print("8. Import XML report")
    print("9. Exit")
    print("================================")


def main():
    
    data_loaded = load_saved_data()
    if data_loaded and not DATA_FILE.exists():
        save_saved_data()

    print("Welcome to the Focus Session Manager")
    if data_loaded:
        print(f"Loaded {len(sessions)} saved session(s).")
    else:
        print("The saved XML file could not be loaded. Starting with empty data.")

    while True:
        print_menu()
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            start_cli_session()
        elif choice == "2":
            stop_cli_session()
        elif choice == "3":
            view_sessions()
        elif choice == "4":
            show_productivity_summary()
        elif choice == "5":
            show_focus_tip()
        elif choice == "6":
            suggest_offline_activity()
        elif choice == "7":
            export_cli_report()
        elif choice == "8":
            import_cli_report()
        elif choice == "9":
            if current_session is not None:
                print("Finish the active session before exiting.")
            else:
                save_saved_data()
                print("Goodbye.")
                break
        else:
            print("Invalid choice. Please select a number from 1 to 9.")


if __name__ == "__main__":
    main()


