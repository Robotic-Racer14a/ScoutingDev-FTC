import ftcOPRMethods as opr

# --- Example Usage ---

opr.event_key = "YEAR/key"
scouting_trust = 5 # How much to trust our data vs calculated OPR

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["data",])
team_objectives = opr.get_event_matches_team_objectives(["objective",])
teams = opr.get_event_teams()

scouted = opr.get_match_data() # Data in form ("frc####", "qm##"): (autoBranchCount, autoTroughCount, teleopBranchCount, teleopTroughCount, netAlgaeCount)
#For pit scouting, use this example ("frc2337", 0): (3, 0, 17, 1, 0)

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