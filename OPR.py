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

#Picking Info
team_picking = 9933
auto_ran_basket = True
tele_basket = True

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
team_a_score = (a_sample[team_picking] * 8) if auto_ran_basket else (a_spec[team_picking] * 10)
team_dc_score = (dc_sample[team_picking] * 8) if tele_basket else (dc_spec[team_picking] * 10)
team_objective_score = a_park[team_picking] + dc_park[team_picking]
for team in teams:
    a_sample_score = a_sample[team] * 8
    a_spec_score = a_spec[team] * 10
    dc_sample_score = dc_sample[team] * 8
    dc_spec_score = dc_spec[team] * 10
    
    a_park_score = a_park[team]
    dc_park_score = dc_park[team]
    
    
    #Auto Part of Pick List
    a_team_with_picking = team_a_score
    a_team_anti_picking = 0
    
    if auto_ran_basket:
        a_team_with_picking += a_spec_score
        a_team_anti_picking = a_sample_score
    else:
        a_team_with_picking += a_sample_score
        a_team_anti_picking = a_spec_score
        
    auto_score = max(a_team_with_picking, a_team_anti_picking)
    
    #Tele Part of Pick List
    dc_team_with_picking = team_dc_score
    dc_team_anti_picking = (team_dc_score * .7)
    
    if tele_basket:
        dc_team_with_picking += dc_spec_score
        dc_team_anti_picking += (dc_sample_score * .7)
    else:
        dc_team_with_picking += dc_sample_score
        dc_team_anti_picking += (dc_spec_score * .7)
        
    tele_score = max(dc_team_with_picking, dc_team_anti_picking)
    
    compiled_score.append({
        "Team": team,
        "Clip Score": a_spec_score + dc_spec_score + a_park_score + dc_park_score,
        "Basket Score": a_sample_score + dc_sample_score + a_park_score + dc_park_score,
        "Total Score": (a_sample_score if a_sample_score > a_spec_score else a_spec_score) + (dc_sample_score if dc_sample_score > dc_spec_score else dc_spec_score) + a_park_score + dc_park_score,
        "Team Pick List": auto_score + tele_score + a_park_score + dc_park_score + team_objective_score,
    })

opr.print_results(compiled_score, "Team Pick List", 50, 1, True)