from multiprocessing import Pool
from astropy import coordinates
import requests

GRADES = ["a","b","c"]
DATA_DIRECTORY = "../data/legacy_survey/"
BASE_URL = "https://www.legacysurvey.org/viewer/fits-cutout"
PIXSCALE = 0.265
FILENAME_ROUND_PLACES = 8

def request_fits(band: str, layer: str, ra: float, dec: float, pixscale: float, file_output: str) -> str:
    """
    Uses the legacysurvey API at legacysurvey.org to get a specific portion of the sky as a .fits file.

    Returns the content of the fits file
    """
    parameters = {
        "ra": ra,
        "dec": dec,
        "band": band,
        "pixscale": pixscale,
        # "layer": layer,
        "height": 256,
        "width": 256
    }

    fits_request = requests.get(BASE_URL, parameters)

    if fits_request.content == 'no such layer':
        raise "Error: Layer not found"

    open(file_output, 'wb').write(fits_request.content)


def get_huang_candidates():
    """ 
    Takes the raw candidates files (with a list of single lines of coordinates) and parses them into their coordinates.

    Returns a list of candidates after they have been parsed as FitsCoordinates objects.

    Choosing not to MapReduce this since the number of candidates that we have to parse is finite and non-massive.
    """
    candidates_list = []
    for grade in GRADES:

        candidates_file = DATA_DIRECTORY + f"huang_grade_{grade}_candidates.txt"

        file_contents = open(candidates_file, 'r').read()

        candidates = file_contents.split('\n')

        for candidate in candidates:
            ra = candidate[5:13]
            dec = candidate[13:21]
            candidates_list.append({
                'ra': ra,
                'dec': dec,
                'grade': grade
            })

    return candidates_list

def request_multiple_fits_parallel(ra_array, dec_array, output_folder, threads = 2):
    """
    Requests multiple FITs cutouts from the API with the respective ra and cutouts.
    Parallelizes this operation onto multiple threads if told to do so.
    """
    # This is ugly, but otherwise it doesn't seem like multiprocessing supports this sort of currying.
    global request_fits_lambda

    def request_fits_lambda(coords):
        (ra, dec) = coords
        filename = f"{output_folder}{str(round(ra, FILENAME_ROUND_PLACES))}_{str(round(dec, FILENAME_ROUND_PLACES))}.fits"
        
        request_fits("ls-dr9", "grz", ra, dec, PIXSCALE, filename)

    coordinates = []
    for i in range(ra_array.shape[0]):
        coordinates.append((ra_array[i], dec_array[i]))
    with Pool(processes=threads) as pool:
        return pool.map(request_fits_lambda, coordinates)