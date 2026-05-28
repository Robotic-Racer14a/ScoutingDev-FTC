import ftcOPRMethods as opr

def combine_match_and_pit(match_data, pit_data):
    scout_data = {}
    for key, data in match_data.items():
        scout_data[key] = data
        
    for key, data in pit_data.items():
        scout_data[key] = data
        
    return scout_data

# --- Example Usage ---

opr.event_key = "YEAR/key"
scouting_trust = 5 # How much to trust our data vs calculated OPR

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["data",])
team_objectives = opr.get_event_matches_team_objectives(["objective",])
teams = opr.get_event_teams()

match_scouted = opr.get_match_data() 
pit_scouted = opr.get_pit_data()
scouted = combine_match_and_pit(match_scouted, pit_scouted)

data_scores = opr.calculate_opr_weighted_per_match(alliance_scores["data"], teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)

objective_scores = opr.calculate_team_average(team_objectives["objective"], teams, {"Yes": 3, "No": 0})


compiled_score = []
for team in teams:
    data_score = data_scores[team]
    objective_score = objective_scores[team]
    
    compiled_score.append({
        "Team": team,
        "Data Score": data_score,
        "Objective Score": objective_score,
        "Total Score": data_score + objective_score,
    })

opr.print_results(compiled_score, "Total Score", 50, 1, True)