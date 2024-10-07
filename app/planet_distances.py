from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
import numpy as np
import pandas as pd
from itertools import combinations

def get_planets_data(planet_names):
    planet_names_sql = "(" + ", ".join(f"'{name}'" for name in planet_names) + ")"

    query = f"pl_name IN {planet_names_sql}"
    results = NasaExoplanetArchive.query_criteria(
        table="ps",
        select="pl_name, ra, dec, sy_dist",  
        where=query  
    )

    df = results.to_pandas().drop_duplicates().reset_index(drop=True)
    return df

def spherical_to_cartesian(ra_deg, dec_deg, dist_pc):
    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)
    
    x = dist_pc * np.cos(ra_rad) * np.cos(dec_rad)
    y = dist_pc * np.sin(ra_rad) * np.cos(dec_rad)
    z = dist_pc * np.sin(dec_rad)
    
    return x, y, z

def calculate_distance(x1, y1, z1, x2, y2, z2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def get_distances(df_pl):
    distance_data = []

    # Iterate through all pairs of planets (including reverse pairs)
    for i, planet_1 in df_pl.iterrows():
        for j, planet_2 in df_pl.iterrows():
            # Skip the case where we compare the same planet to itself
            if i != j:
                # Get Cartesian coordinates of the two planets
                x1, y1, z1 = planet_1['x'], planet_1['y'], planet_1['z']
                x2, y2, z2 = planet_2['x'], planet_2['y'], planet_2['z']

                # Calculate the distance between the two planets
                distance = calculate_distance(x1, y1, z1, x2, y2, z2)

                # Append the results to the list (A to B and B to A)
                distance_data.append({
                    'P1': planet_1['pl_name'],
                    'P2': planet_2['pl_name'],
                    'D': distance
                })

    # Convert the list to a new DataFrame
    df_dist = pd.DataFrame(distance_data)
    return df_dist

def get_closest_planets(df_pl, df_dist):
    # Initialize a list to hold the results for the DataFrame
    results = []

    # Iterate through each planet in df_pl
    for planet in df_pl['pl_name']:
        # Get the distance to Earth for the current planet
        sy_dist = df_pl.loc[df_pl['pl_name'] == planet, 'sy_dist'].values[0]

        # Filter the distances where the current planet is directly referenced
        distances = df_dist[df_dist['P1'] == planet]

        # Sort by distance and get the top 3 closest planets
        closest_planets = distances.sort_values(by='D').head(3)

        # Prepare a row with the planet name, distance to Earth, and the closest planets
        row = {
            'Planet Name': planet,
            'Distance to Earth (parsecs)': sy_dist  # Add the distance to Earth
        }

        # Populate closest planet names and distances
        for i in range(len(closest_planets)):
            row[f'Closest Planet {i + 1}'] = closest_planets.iloc[i]['P2']
            row[f'Distance {i + 1} (parsecs)'] = closest_planets.iloc[i]['D']

        # If there are less than 3 closest planets, fill with None
        for j in range(len(closest_planets), 3):
            row[f'Closest Planet {j + 1}'] = None
            row[f'Distance {j + 1} (parsecs)'] = None
        
        # Append the row to results
        results.append(row)

    # Convert the results into a DataFrame
    closest_planets_df = pd.DataFrame(results)

    return closest_planets_df

################################ Code Execution ################################

planet_names = [
    "Proxima Cen b",
    "TRAPPIST-1 g",
    "Gliese 12 b",
    "GJ 273 b",
    "GJ 581 c",
    "K2-18 b",
    "K2-72 e",
    "Kepler-22 b",
    "Kepler-62 f",
    "Kepler-69 c",
    "Kepler-442 b",
    "HD 40307 g",
    "55 Cnc e",
    "Teegarden''s Star d",
    "LHS 1140 b",
    "6 Lyn b",
    "TOI-2257 b",
    "Wolf 1069 b"
]


df_pl = get_planets_data(planet_names)

df_pl.loc[df_pl['pl_name'] == 'TRAPPIST-1 g', 'sy_dist'] = 12.4298888

df_pl[['x', 'y', 'z']] = df_pl.apply(
    lambda row: spherical_to_cartesian(row['ra'], row['dec'], row['sy_dist']), axis=1, result_type='expand'
)


df_dist = get_distances(df_pl)

df_closest = get_closest_planets(df_pl, df_dist)

df_closest.to_excel("../data/closest.xlsx", index=False)
