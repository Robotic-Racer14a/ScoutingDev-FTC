import ftcOPRMethods as opr

def combine_match_and_pit(match_data, pit_data):
    scout_data = {}
    for key, data in match_data.items():
        scout_data[key] = data
        
    for key, data in pit_data.items():
        scout_data[key] = data
        
    return scout_data

# --- Example Usage ---

opr.event_key = "2023/USMICMPFLWR"
scouting_trust = 5 # How much to trust our data vs calculated OPR

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["autoBackdrop", "dcBackdrop"])
team_objectives = opr.get_event_matches_team_objectives(["autoNav", "purple", "yellow", "egNav2023_", "drone"])
teams = opr.get_event_teams()

match_scouted = opr.get_match_data() 
pit_scouted = opr.get_pit_data()
scouted = combine_match_and_pit(match_scouted, pit_scouted)

a_bd = opr.calculate_opr_weighted_per_match(alliance_scores["autoBackdrop"], teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)
dc_bd = opr.calculate_opr_weighted_per_match(alliance_scores["dcBackdrop"], teams, {key: value[1] for key, value in scouted.items()}, scouting_trust)

a_nav = opr.calculate_team_average(team_objectives["autoNav"], teams, {True: 5, False: 0})
purple = opr.calculate_team_average(team_objectives["purple"], teams, {"Pixel": 10, "TeamProp": 20, "None": 0})
yellow = opr.calculate_team_average(team_objectives["yellow"], teams, {"Pixel": 10, "TeamProp": 20, "None": 0})
eg_nav = opr.calculate_team_average(team_objectives["egNav2023_"], teams, {"Rigging": 20, "Backstage": 5, "None": 0})
drone = opr.calculate_team_average(team_objectives["drone"], teams, {3: 30, 2: 20, 1: 10, 0: 0})


compiled_score = []
for team in teams:
    a_bd_score = a_bd[team] * 5
    dc_bd_score = dc_bd[team] * 3
    a_nav_score = a_nav[team]
    eg_nav_score = eg_nav[team]
    purple_score = purple[team]
    yellow_score = yellow[team]
    drone_score = drone[team]
    setline_score = ((a_bd[team] + dc_bd[team]) // 8) * 10
    
    auto = purple_score + yellow_score + a_bd_score + a_nav_score
    tele = dc_bd_score + setline_score
    end = drone_score + eg_nav_score
    
    compiled_score.append({
        "Team": team,
        "Auto Score": auto,
        "Tele Score": tele,
        "Endgame Score": end,
        "Total Score": auto + tele + end,
    })

opr.print_results(compiled_score, "Total Score", 50, 1, True)