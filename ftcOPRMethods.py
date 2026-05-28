import numpy as np
import requests
import shelve

BASE_URL = "https://api.ftcscout.org/rest/v1"

event_key = ""

def clear_match_data(key = None):
    with shelve.open("scouting") as db:
        if key == None:
            db[event_key] = {}
        else:
            new_list = {}
            for key, value in db[event_key].items():
                if key != key:
                    new_list[key] = value
            db[event_key] = new_list
        
def clear_match_all():
    with shelve.open("scouting") as db:
        db.clear()

def add_match_data(data):
    with shelve.open("scouting") as db:
        try:
            previous_data = db[event_key]
        except KeyError:
            previous_data = {}
            
        for key, value in data.items():
            previous_data[key] = value
        db[event_key] = previous_data
    
def get_match_data():
    with shelve.open("scouting") as db:
        try:
            return db[event_key]
        except KeyError:
            return {}
        
def clear_pit_data(key = None):
    with shelve.open("pit_scouting") as db:
        if key == None:
            db[event_key] = {}
        else:
            new_list = {}
            for key, value in db[event_key].items():
                if key != key:
                    new_list[key] = value
            db[event_key] = new_list
        
def clear_pit_all():
    with shelve.open("pit_scouting") as db:
        db.clear()

def add_pit_data(data):
    with shelve.open("pit_scouting") as db:
        try:
            previous_data = db[event_key]
        except KeyError:
            previous_data = {}
            
        for key, value in data.items():
            previous_data[key] = value
        db[event_key] = previous_data
    
def get_pit_data():
    with shelve.open("pit_scouting") as db:
        try:
            return db[event_key]
        except KeyError:
            return {}

def print_match_options():
    url = f"{BASE_URL}/events/{event_key}/matches"
    response = requests.get(url)
    response.raise_for_status()
    matches = response.json()
    print(matches[0]["scores"]["red"])
    

def get_event_matches_alliance_scores(criteras):
    url = f"{BASE_URL}/events/{event_key}/matches"
    response = requests.get(url)
    response.raise_for_status()
    matches = response.json()
    matchList = {}
    for critera in criteras:
        critera_list = []
        for match in matches:
            critera_list.append({
                "red_teams": [match["teams"][0]["teamNumber"], match["teams"][1]["teamNumber"]],
                "red_score": match["scores"]["red"][critera],
                "blue_teams": [match["teams"][2]["teamNumber"], match["teams"][3]["teamNumber"]],
                "blue_score": match["scores"]["blue"][critera],
                "match_key": match["id"]
                })
        matchList[critera] = critera_list
    return matchList

def get_event_matches_team_objectives(criteras):
    url = f"{BASE_URL}/events/{event_key}/matches"
    response = requests.get(url)
    response.raise_for_status()
    matches = response.json()
    matchList = {}
    for critera in criteras:
        critera_list = []
        for match in matches:
            critera_list.append({
                "red_one": [match["teams"][0]["teamNumber"], match["scores"]["red"][f"{critera}1"]],
                "red_two": (match["teams"][1]["teamNumber"], match["scores"]["red"][f"{critera}2"]),
                "blue_one": (match["teams"][2]["teamNumber"], match["scores"]["blue"][f"{critera}1"]),
                "blue_two": (match["teams"][3]["teamNumber"], match["scores"]["blue"][f"{critera}2"]),
                "match_key": match["id"]
                })
        matchList[critera] = critera_list
    return matchList

def get_event_teams():
    url = f"{BASE_URL}/events/{event_key}/teams"
    response = requests.get(url)
    response.raise_for_status()
    teams =  response.json()
    teamList = []
    for team in teams:
        teamList.append(team["teamNumber"])
    return teamList

def print_results(results, sort_key, number_of_teams, break_threshold, invert):
    if invert:
        results.sort(key=lambda x: -x[sort_key])
    else:
        results.sort(key=lambda x: x[sort_key])
    prevResult = 0
    print(f"\n\n\n\n{sort_key}")
    for i in range(len(results)):
        if i >= number_of_teams:
            break
        result = results[i]
        if(invert and prevResult - result[sort_key] > break_threshold): 
            print("")
        elif (not invert and result[sort_key] - prevResult > break_threshold):
            print("")
        print(f"{i + 1}: {result["Team"]}: {result[sort_key]}")
        prevResult = result[sort_key]

def calculate_opr_weighted_per_match(matches, teams, scouted_scores = {}, scout_weight=5.0):
    team_index = {team: i for i, team in enumerate(teams)}
    n = len(teams)
    valid_match_keys = {item["match_key"] for item in matches}

    # Collect pit-scouted zeroes: teams known to score 0 for a specific metric
    pit_zero_teams = {
        team for (team, match_i), observed_score in scouted_scores.items()
        if match_i not in valid_match_keys and observed_score == 0
    }

    A, b = [], []

    # Standard match rows — but redistribute credit away from pit-zeroed teams
    for match in matches:
        for color in ['red', 'blue']:
            alliance_teams = match[f'{color}_teams']
            alliance_score = match[f'{color}_score']
            zeroed = [t for t in alliance_teams if t in pit_zero_teams and t in team_index]
            active  = [t for t in alliance_teams if t not in pit_zero_teams and t in team_index]

            if zeroed:
                # Pin each zeroed team to 0 in this match
                for t in zeroed:
                    pin_row = [0] * n
                    pin_row[team_index[t]] = scout_weight
                    A.append(pin_row)
                    b.append(0.0)

                # Give full alliance score to the remaining teammates
                if active:
                    residual_row = [0] * n
                    for t in active:
                        residual_row[team_index[t]] = 1
                    A.append(residual_row)
                    b.append(alliance_score)
                # If the entire alliance is zeroed (edge case), still add the standard row
                # so the system isn't underdetermined — score just won't be redistributed
                else:
                    row = [0] * n
                    for t in alliance_teams:
                        if t in team_index:
                            row[team_index[t]] = 1
                    A.append(row)
                    b.append(alliance_score)
            else:
                # Normal row — no pit-zeroed teams on this alliance
                row = [0] * n
                for t in alliance_teams:
                    if t in team_index:
                        row[team_index[t]] = 1
                A.append(row)
                b.append(alliance_score)

    # Per-match scouting rows
    for (team, match_i), observed_score in scouted_scores.items():
        if team not in team_index:
            continue
        if observed_score is None or observed_score < 0:
            continue

        if match_i not in valid_match_keys:
            # Ignore Pit scouting data in match data
            continue

        # In-match scouting
        match = next(item for item in matches if item["match_key"] == match_i)
        all_teams = match['red_teams'] + match['blue_teams']
        if team not in all_teams:
            print(f"Warning: team {team} not in match {match_i}, skipping.")
            continue

        row = [0] * n
        row[team_index[team]] = scout_weight
        A.append(row)
        b.append(observed_score * scout_weight)

    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    opr_values, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return {team: opr_values[i] for team, i in team_index.items()}

def calculate_team_average(matches, teams, correct_keys):
    team_totals = {team: {"total": 0, "count": 0} for team in teams}

    alliance_keys = ["red_one", "red_two", "blue_one", "blue_two"]

    for match in matches:
        for key in alliance_keys:
            if key in match:
                team_num, score = match[key]
                
                if score in correct_keys:
                    point_score = correct_keys[score]
                else:
                    print(score)
                    point_score = 0
                    
                if team_num in team_totals:
                    team_totals[team_num]["total"] += point_score
                    team_totals[team_num]["count"] += 1

    return {
        team: (data["total"] / data["count"] if data["count"] > 0 else 0)
        for team, data in team_totals.items()
    }