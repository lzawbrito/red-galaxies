from api.legacy_survey import get_huang_candidates
import pandas as pd

candidates = get_huang_candidates()
df = pd.DataFrame(candidates)

df.to_csv('../files/all_huang_candidates.csv')