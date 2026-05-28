import ftcOPRMethods as opr

def combine_match_and_pit(match_data, pit_data):
    scout_data = {}
    for key, data in match_data.items():
        
        if pit_data[(key[0], "PIT")][0] == "High":
            a_low_bas = 0
            a_high_bas = data[0]
        else:
            a_low_bas = data[0]
            a_high_bas = 0
           
        if pit_data[(key[0], "PIT")][1] == "High":
            a_low_cli = 0
            a_high_cli = data[1]
        else:
            a_low_cli = data[1]
            a_high_cli = 0
           
        if pit_data[(key[0], "PIT")][0] == "High":
            dc_low_bas = 0
            dc_high_bas = data[2]
        else:
            dc_low_bas = data[2]
            dc_high_bas = 0
           
        if pit_data[(key[0], "PIT")][1] == "High":
            dc_low_cli = 0
            dc_high_cli = data[3]
        else:
            dc_low_cli = data[3]
            dc_high_cli = 0
            
        scout_data[key] = (a_low_bas, a_high_bas, a_low_cli, a_high_cli, dc_low_bas, dc_high_bas, dc_low_cli, dc_high_cli)
        
    for key, data in pit_data.items():
        if data[0] == "High":
            a_low_bas = 0
            a_high_bas = 1
        else:
            a_low_bas = 1
            a_high_bas = 0
           
        if data[1] == "High":
            a_low_cli = 0
            a_high_cli = 1
        else:
            a_low_cli = 1
            a_high_cli = 0
           
        if data[0] == "High":
            dc_low_bas = 0
            dc_high_bas = 1
        else:
            dc_low_bas = 1
            dc_high_bas = 0
           
        if data[1] == "High":
            dc_low_cli = 0
            dc_high_cli = 1
        else:
            dc_low_cli = 1
            dc_high_cli = 0
            
        scout_data[key] = (a_low_bas, a_high_bas, a_low_cli, a_high_cli, dc_low_bas, dc_high_bas, dc_low_cli, dc_high_cli)
        
    return scout_data

def estimate_missing_pit(prelim_opr_low_clip, prelim_opr_high_clip, prelim_opr_low_basket, prelim_opr_high_basket, pit_data):
    new_pit_data = {}
    for team, high_clip_score in prelim_opr_high_clip.items():
        if (team, "PIT") in pit_data:
            new_pit_data[(team, "PIT")] = pit_data[(team, "PIT")]
        else:
            low_clip_score = prelim_opr_low_clip[team]
            high_basket_score = prelim_opr_high_basket[team]
            low_basket_score = prelim_opr_low_basket[team]
            
            if high_basket_score > 1:
                basket_score = "High"
            elif low_basket_score > 1:
                basket_score = "Low"
            else:
                basket_score = "None"
            
            if high_clip_score > 1:
                clip_score = "High"
            elif low_clip_score > 1:
                clip_score = "Low"
            else:
                clip_score = "None"
            new_pit_data[(team, "PIT")] = (basket_score, clip_score)
            
    return new_pit_data

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

match_scouted = opr.get_match_data() 
pit_scouted = opr.get_pit_data()
scouted = combine_match_and_pit(match_scouted, pit_scouted)

a_sample_low = opr.calculate_opr_weighted_per_match(alliance_scores["autoSampleLow"], teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)
a_sample_high = opr.calculate_opr_weighted_per_match(alliance_scores["autoSampleHigh"], teams, {key: value[1] for key, value in scouted.items()}, scouting_trust)
a_spec_low = opr.calculate_opr_weighted_per_match(alliance_scores["autoSpecimenLow"], teams, {key: value[2] for key, value in scouted.items()}, scouting_trust)
a_spec_high = opr.calculate_opr_weighted_per_match(alliance_scores["autoSpecimenHigh"], teams, {key: value[3] for key, value in scouted.items()}, scouting_trust)
dc_sample_low = opr.calculate_opr_weighted_per_match(alliance_scores["dcSampleLow"], teams, {key: value[4] for key, value in scouted.items()}, scouting_trust)
dc_sample_high = opr.calculate_opr_weighted_per_match(alliance_scores["dcSampleHigh"], teams, {key: value[5] for key, value in scouted.items()}, scouting_trust)
dc_spec_low = opr.calculate_opr_weighted_per_match(alliance_scores["dcSpecimenLow"], teams, {key: value[6] for key, value in scouted.items()}, scouting_trust)
dc_spec_high = opr.calculate_opr_weighted_per_match(alliance_scores["dcSpecimenHigh"], teams, {key: value[7] for key, value in scouted.items()}, scouting_trust)

a_park = opr.calculate_team_average(team_objectives["autoPark"], teams, {"ObservationZone": 3, "Ascent1": 3, "None": 0})
dc_park = opr.calculate_team_average(team_objectives["autoPark"], teams, {"Ascent3": 30, "Ascent2": 15, "ObservationZone": 3, "Ascent1": 3, "None": 0})


compiled_score = []
team_a_score = (a_sample_high[team_picking] * 8) if auto_ran_basket else (a_spec_high[team_picking] * 10)
team_dc_score = (dc_sample_high[team_picking] * 8) if tele_basket else (dc_spec_high[team_picking] * 10)
team_objective_score = a_park[team_picking] + dc_park[team_picking]
for team in teams:
    a_sample_score = a_sample_high[team] * 8
    a_spec_score = a_spec_high[team] * 10
    dc_sample_score = dc_sample_high[team] * 8
    dc_spec_score = dc_spec_high[team] * 10
    
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