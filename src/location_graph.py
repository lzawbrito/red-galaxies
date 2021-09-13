import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
import astropy.coordinates as coord
import astropy.units as u

red_galaxy_data = pd.read_csv("../red-galaxies/all_red_galaxies.txt") #in radians
known_lens_data = pd.read_csv("../red-galaxies/all_huang_candidates_formatted.txt") # in degrees

ra_known, dec_known = known_lens_data["ra"], known_lens_data["dec"]
ra_red_galaxy, dec_red_galaxy = red_galaxy_data["ra"], red_galaxy_data["dec"]

ra = coord.Angle(ra_known * u.degree)
ra = ra.wrap_at(180 * u.degree)
dec = coord.Angle(dec_known * u.degree)

fig = plt.figure(figsize=(9,9))

ax = fig.add_subplot(111, projection= "mollweide")
ax.scatter(ra.radian, dec.radian, s=1, c='black', marker='o')

# Red-Galaxies
# first convert radians to degrees
def rad2deg(x):
    return (180 * x) / np.pi

ra_red_galaxy = ra_red_galaxy.apply(rad2deg)
dec_red_galaxy = dec_red_galaxy.apply(rad2deg) 

ra_red = coord.Angle(ra_red_galaxy * u.degree)
ra_red = ra_red.wrap_at(180 * u.degree)
dec_red = coord.Angle(dec_red_galaxy * u.degree)

ax.scatter(ra_red.radian, dec_red.radian, s=1, c='red' , marker='o')
ax.set_ylabel("DEC")
ax.set_xlabel("RA")
ax.legend(["Huang Known Lenses", "Dell`Antonio Red Galaxies"], loc="upper center", markerscale=5)
ax.title.set_text("Known Gravitational Lenses and Red Galaxies in Dell'Antonio's Survey")

ax.grid(True)
plt.show()
