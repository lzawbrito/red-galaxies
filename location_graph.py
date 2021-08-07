import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
import astropy.coordinates as coord
import astropy.units as u

red_galaxy_data = pd.read_csv("../data/all_red_galaxies.csv")
known_lens_data = pd.read_csv("../data/legacy_survey/all_huang_candidates_formatted.csv")

ra_known, dec_known = known_lens_data["ra"], known_lens_data["dec"]
ra_red_galaxy, dec_red_galaxy = red_galaxy_data["ra"], red_galaxy_data["dec"]

ra = coord.Angle(ra_known * u.degree)
ra = ra.wrap_at(180 * u.degree)
dec = coord.Angle(dec_known * u.degree)

fig = plt.figure(figsize=(6,6))

ax = fig.add_subplot(111, projection= "mollweide")
ax.scatter(ra.radian, dec.radian, s=5, c='black')

# Red-Galaxies
ra_red = coord.Angle(ra_red_galaxy * u.degree)
ra_red = ra_red.wrap_at(180 * u.degree)
dec_red = coord.Angle(dec_red_galaxy * u.degree)

ax.scatter(ra_red.radian, dec_red.radian, s=5, c='red')
ax.legend(["Known Lenses", "Local Red Galaxies"])
ax.title.set_text("Local Red Galaxies (Red) vs. Lnown Gravitational Lenses (Black)")

ax.grid(True)
plt.show()