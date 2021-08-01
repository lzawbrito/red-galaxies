import requests

GRADES = ["a","b","c"]

DATA_DIRECTORY = "../data/legacy_survey/"

BASE_URL = "https://www.legacysurvey.org/viewer/fits-cutout"

# TODO: What are 'ra', 'dec'?? They seem to be tempermental and cause 500 errors if their values are wrong
# TODO: Make this store directly into a variable so we don't have to write it to a file
def request_fits(band: str, layer: str, ra: float, dec: float, pixscale: float, file_output: str) -> str:
    """
    Uses the legacysurvey API at legacysurvey.org to get a specific portion of the sky as a .fits file.

    Returns the content of the fits file
    """
    # TODO: layer seems to break things (same behavior in the browser)
    parameters = {
        "ra": ra,
        "dec": dec,
        "band": band,
        "pixscale": pixscale,
        # "layer": layer
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
