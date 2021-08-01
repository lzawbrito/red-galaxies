import pandas as pd

galaxies = pd.read_csv('files/all_galaxies.csv')

galaxies = galaxies[galaxies["z_mag"] < 21.0172]
galaxies = galaxies[galaxies["z_mag"] > 15.859]
galaxies = galaxies[galaxies["g_mag"] < 23.758]
galaxies = galaxies[galaxies["g_mag"] > 18.6]
galaxies = galaxies[galaxies["r_mag"] < 22.2022]
galaxies = galaxies[galaxies["r_mag"] > 17.0446]

print(len(galaxies))

