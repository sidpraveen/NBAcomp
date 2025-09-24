from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pandas as pd

# -------------------------
# Dictionary of Career Accolades (expandable)
# -------------------------
accolades = {
    "LeBron James": {"Championships": 4, "Finals MVPs": 4, "MVPs": 4},
    "Kevin Durant": {"Championships": 2, "Finals MVPs": 2, "MVPs": 1},
    "Stephen Curry": {"Championships": 4, "Finals MVPs": 1, "MVPs": 2},
    "Michael Jordan": {"Championships": 6, "Finals MVPs": 6, "MVPs": 5},
    "Tim Duncan": {"Championships": 5, "Finals MVPs": 3, "MVPs": 2},
    "Shaquille O'Neal": {"Championships": 4, "Finals MVPs": 3, "MVPs": 1},
    "Kobe Bryant": {"Championships": 5, "Finals MVPs": 2, "MVPs": 1},
    "Dirk Nowitzki": {"Championships": 1, "Finals MVPs": 1, "MVPs": 1},
    "Dwyane Wade": {"Championships": 3, "Finals MVPs": 1, "MVPs": 0},
    "Kareem Abdul-Jabbar": {"Championships": 6, "Finals MVPs": 2, "MVPs": 6},
    "Wilt Chamberlain": {"Championships": 2, "Finals MVPs": 1, "MVPs": 4},
    "Bill Russell": {"Championships": 11, "Finals MVPs": 1, "MVPs": 5},
    "Larry Bird": {"Championships": 3, "Finals MVPs": 2, "MVPs": 3},
    "Magic Johnson": {"Championships": 5, "Finals MVPs": 3, "MVPs": 3},
    "Kevin Garnett": {"Championships": 1, "Finals MVPs": 0, "MVPs": 1},
    "Tracy McGrady": {"Championships": 0, "Finals MVPs": 0, "MVPs": 0},
    "Hakeem Olajuwon": {"Championships": 2, "Finals MVPs": 2, "MVPs": 1},
    "Damian Lillard": {"Championships": 0, "Finals MVPs": 0, "MVPs": 0},
    "Giannis Antetokounmpo": {"Championships": 1, "Finals MVPs": 1, "MVPs": 2},
    "Nikola Jokic": {"Championships": 1, "Finals MVPs": 1, "MVPs": 3},
    "Russell Westbrook": {"Championships": 0, "Finals MVPs": 0, "MVPs": 1},
    "James Harden": {"Championships": 0, "Finals MVPs": 0, "MVPs": 1},
    "Kawhi Leonard": {"Championships": 2, "Finals MVPs": 2, "MVPs": 0}
}

# -------------------------
# Helper Functions
# -------------------------
def normalize_name(name):
    """Standardize player names for accolade lookup."""
    return name.strip().title()

def get_player_id(name):
    """Find a player's NBA ID given their name."""
    player_dict = players.find_players_by_full_name(name)
    if len(player_dict) == 0:
        return None
    return player_dict[0]["id"]

def get_player_stats(name):
    """Get career per-season per-game stats for a player."""
    player_id = get_player_id(name)
    if not player_id:
        print("Player {name} not found!")
        return None

    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]

    # Convert totals → per-game values
    df["PTS"] = df["PTS"] / df["GP"]
    df["AST"] = df["AST"] / df["GP"]
    df["REB"] = df["REB"] / df["GP"]
    df["STL"] = df["STL"] / df["GP"]
    df["BLK"] = df["BLK"] / df["GP"]

    return df[[
        "SEASON_ID", "GP", "PTS", "AST", "REB", "STL", "BLK", "FG_PCT", "FG3_PCT"
    ]]

def compute_career_averages(df):
    """Compute weighted career per-game averages."""
    total_gp = df["GP"].sum()

    def weighted_avg(col):
        return (df[col] * df["GP"]).sum() / total_gp if total_gp > 0 else 0

    return {
        "PTS": round(weighted_avg("PTS"), 1),
        "AST": round(weighted_avg("AST"), 1),
        "REB": round(weighted_avg("REB"), 1),
        "STL": round(weighted_avg("STL"), 1),
        "BLK": round(weighted_avg("BLK"), 1),
        "FG%": round(weighted_avg("FG_PCT") * 100, 1),
        "3P%": round(weighted_avg("FG3_PCT") * 100, 1),
    }

# -------------------------
# Comparison Logic
# -------------------------
def compare_players(name1, name2):
    stats1 = get_player_stats(name1)
    stats2 = get_player_stats(name2)

    if stats1 is None or stats2 is None:
        print("Comparison failed. Check player names.")
        return

    avg1 = compute_career_averages(stats1)
    avg2 = compute_career_averages(stats2)

    print("Career Averages:")
    df_compare = pd.DataFrame({name1: avg1, name2: avg2})
    print(df_compare)

    # Category winners
    print("Stat Category Winners:")
    score1, score2 = 0, 0
    for cat in avg1.keys():
        if avg1[cat] > avg2[cat]:
            print(f"{cat}: {name1} wins ({avg1[cat]} vs {avg2[cat]})")
            score1 += 1
        elif avg2[cat] > avg1[cat]:
            print(f"{cat}: {name2} wins ({avg2[cat]} vs {avg1[cat]})")
            score2 += 1
        else:
            print(f"{cat}: Tie ({avg1[cat]} vs {avg2[cat]})")

    # Accolades comparison
    print("Career Accolades:")
    acc1 = accolades.get(normalize_name(name1), {"Championships": "N/A", "Finals MVPs": "N/A", "MVPs": "N/A"})
    acc2 = accolades.get(normalize_name(name2), {"Championships": "N/A", "Finals MVPs": "N/A", "MVPs": "N/A"})
    print(f"{name1}: {acc1}")
    print(f"{name2}: {acc2}")

    # Final verdict
    print("Final Verdict:")
    if score1 > score2:
        print(f"{name1} is the better statistical player ({score1}-{score2})")
    elif score2 > score1:
        print(f"{name2} is the better statistical player ({score2}-{score1})")
    else:
        print("Stats are tied. Accolades decide:")
        if acc1["Championships"] != "N/A" and acc2["Championships"] != "N/A":
            if acc1["Championships"] > acc2["Championships"]:
                print(f"{name1} wins on championships.")
            elif acc2["Championships"] > acc1["Championships"]:
                print(f"{name2} wins on championships.")
            else:
                print("Even accolades. Too close to call!")

# -------------------------
# Run Comparison
# -------------------------
if __name__ == "__main__":
    name1 = input("Enter first NBA player: ")
    name2 = input("Enter second NBA player: ")
    compare_players(name1, name2)










