from import_libs import *
from datetime import datetime, timedelta
def backup_whole_directory(source_folder, backup_folder):
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_folder, f"PalworldSave_backup_{timestamp}")
    shutil.copytree(source_folder, backup_path)
    print(f"Backup of {source_folder} created at: {backup_path}")
def get_number_in_range(min_value, max_value):
  while True:
    try:
      number = int(input(f"Enter a number between {min_value} and {max_value}: "))
      if min_value <= number <= max_value:
        return number
      else:
        print("Number is out of range. Try again.")
    except ValueError:
      print("Invalid input. Please enter an integer.")
def get_directory_from_user():
    while True:
        directory_path = input("Please enter a directory path: ")
        if os.path.isdir(directory_path):
            return directory_path
        else:
            print("Invalid directory path. Please try again.")
def get_filtered_uids(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return {line.strip() for line in file.readlines() if line.strip()}
def extract_player_info(line):
    match = re.search(r'Player: (.+?) \| UID: ([\w-]+) \| .*?Owned: (\d+)', line)
    if match:
        player_name = match.group(1)
        player_uid = match.group(2)
        pals_found = int(match.group(3))
        return player_name, player_uid, pals_found
    return None, None, None
def find_player_uids_with_max_pals(log_file, filtered_uids, max_pals):
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"File '{log_file}' not found.")
        return []
    player_info = []
    for line in lines:
        player_name, player_uid, pals_found = extract_player_info(line)
        if player_uid and player_uid not in filtered_uids and pals_found <= max_pals:
            player_info.append((line.strip(), player_uid, pals_found))
    return player_info
def delete_player_saves(player_info):
    players_folder = "PalworldSave/Players"
    backup_folder = "Backups/Delete Saves by Pals Count"
    if not os.path.exists(players_folder):
        print(f"Players folder '{players_folder}' not found.")
        return
    backup_whole_directory("PalworldSave", backup_folder)
    total_pals_to_delete = sum(pals_found for _, _, pals_found in player_info)
    deleted_count = 0
    players_before = len([f for f in os.listdir(players_folder) if f.endswith(".sav")])
    for line, uid, _ in player_info:
        uid_no_hyphens = uid.replace('-', '')
        sav_filename = f"{uid_no_hyphens}.sav"
        sav_file_paths = [os.path.join(players_folder, f) for f in os.listdir(players_folder) if f.lower() == sav_filename.lower()]
        if sav_file_paths:
            sav_file_path = sav_file_paths[0]
            os.remove(sav_file_path)
            deleted_count += 1
            print(f"Deleted: {sav_file_path}")
            print(f"Deleted Player Info: {line}")
    players_after = len([f for f in os.listdir(players_folder) if f.endswith(".sav")])
    print("=" * 80)
    print(f"Total Players: {players_before}")
    print(f"Total Players Deleted: {deleted_count}")
    print(f"Total Pals Count of Deleted Players: {total_pals_to_delete}")
    print(f"Total Players Kept: {players_after}")
    print(f"Filtered by: Pals <= {max_pals}")
    print("=" * 80)
if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python delete_pals_save.py <log_file>")
        sys.exit(1)
    log_file = sys.argv[1]
    players_folder = os.path.join(os.path.dirname(log_file), 'PalworldSave', 'Players')
    players_count = len([f for f in os.listdir(players_folder) if f.endswith(".sav")])
    print(f"There are {players_count} players in the 'Players' folder.")
    max_pals = int(input("Enter maximum number of pals per player to delete: "))
    filtered_uids = get_filtered_uids('players_filtered.log')
    player_info = find_player_uids_with_max_pals(log_file, filtered_uids, max_pals)
    if player_info: delete_player_saves(player_info)
    else: print(f"No PlayerUIDs found in {log_file} that match the filter.")