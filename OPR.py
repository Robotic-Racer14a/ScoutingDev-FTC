import ftcOPRMethods as opr

def get_total_count(matches_1, matches_2):
    new_list = []
    for i in range(len(matches_1)):
        match_1 = matches_1[i]
        match_2 = matches_2[i]
        new_list.append({
            "red_teams": match_1["red_teams"],
            "red_score": match_1["red_score"] + match_2["red_score"],
            "blue_teams": match_1["blue_teams"],
            "blue_score": match_1["blue_score"] + match_2["blue_score"],
            "match_key": match_1["match_key"]
        })
    return new_list

# --- Example Usage ---

opr.event_key = "2024/USMIGOQ"
scouting_trust = 5 # How much to trust our data vs calculated OPR

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["autoSampleLow", "autoSampleHigh", "autoSpecimenLow", "autoSpecimenHigh", "dcSampleLow", "dcSampleHigh", "dcSpecimenLow", "dcSpecimenHigh"])
team_objectives = opr.get_event_matches_team_objectives(["autoPark", "dcPark"])
teams = opr.get_event_teams()

scouted = opr.get_data() # Data in form ("frc####", "qm##"): (autoBranchCount, autoTroughCount, teleopBranchCount, teleopTroughCount, netAlgaeCount)
#For pit scouting, use this example ("frc2337", 0): (3, 0, 17, 1, 0)

a_sample = opr.calculate_opr_weighted_per_match(get_total_count(alliance_scores["autoSampleLow"], alliance_scores["autoSampleHigh"]), teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)
a_spec = opr.calculate_opr_weighted_per_match(get_total_count(alliance_scores["autoSpecimenLow"], alliance_scores["autoSpecimenHigh"]), teams, {key: value[1] for key, value in scouted.items()}, scouting_trust)
dc_sample = opr.calculate_opr_weighted_per_match(get_total_count(alliance_scores["dcSampleLow"], alliance_scores["dcSampleHigh"]), teams, {key: value[2] for key, value in scouted.items()}, scouting_trust)
dc_spec = opr.calculate_opr_weighted_per_match(get_total_count(alliance_scores["dcSpecimenLow"], alliance_scores["dcSpecimenHigh"]), teams, {key: value[3] for key, value in scouted.items()}, scouting_trust)

a_park = opr.calculate_team_average(team_objectives["autoPark"], teams, {"ObservationZone": 3, "Ascent1": 3, "None": 0})
dc_park = opr.calculate_team_average(team_objectives["autoPark"], teams, {"Ascent3": 30, "Ascent2": 15, "ObservationZone": 3, "Ascent1": 3, "None": 0})


compiled_score = []
for team in teams:
    
    a_sample_score = a_sample[team] * 8
    a_spec_score = a_spec[team] * 10
    dc_sample_score = dc_sample[team] * 8
    dc_spec_score = dc_spec[team] * 10
    
    a_park_score = a_park[team]
    dc_park_score = dc_park[team]
    
    compiled_score.append({
        "Team": team,
        "Clip Score": a_spec_score + dc_spec_score + a_park_score + dc_park_score,
        "Basket Score": a_sample_score + dc_sample_score + a_park_score + dc_park_score,
        "Total Score": a_sample_score + dc_sample_score + a_spec_score + dc_spec_score + a_park_score + dc_park_score,
    })

opr.print_results(compiled_score, "Total Score", 50, 1, True)