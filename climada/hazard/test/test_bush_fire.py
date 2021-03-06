"""
Test Bush fire class
"""

import unittest
import pandas as pd
from datetime import datetime

from climada.hazard.bush_fire import BushFire

description = ''

class TestReaderDF(unittest.TestCase):
    """Test loading functions from the BushFire class for synthetic data"""

    def _read_firms_synth(firms, description=''):
        """Read synthetic files from bushfire data.

        Parameters:
            firms: dataframe with latitude, longitude, acquisition date (acq_date)
            description (str, optional): description of the events

        Returns:
            firms, description
        """
        firms = pd.DataFrame.from_dict(firms)
        for index, acq_date in enumerate(firms['acq_date'].values):
            datetime.strptime(acq_date, '%Y-%m-%d').date()
            datenum = datetime.strptime(acq_date, '%Y-%M-%d').toordinal()
            firms.at[index, 'datenum'] = datenum
        return firms, description


    def test_hist_event_one_pass(self):
        bf = BushFire()
        firms = {'latitude' : [-38.104, -38.104, -38.104, -38.104, -38.104, -38.093, -38.095,
             -37.433, -37.421, -37.423, -37.45, -38.104, -38.104, -38.104,
             -38.095, -37.45, -38.045, -38.047, -38.036, -37.983,
             -37.978, -37.979, -37.981, -37.45, -37.431,
             -37.421, -37.423, -38.104],
        'longitude' : [146.388, 146.388,146.388, 146.388, 146.388, 146.397,
                       146.386, 142.43,142.442, 142.428, 145.361, 146.388,
                       146.388, 146.388,
             146.397, 145.361, 146.416, 146.404, 146.413, 146.33,
             146.311, 146.299, 146.288, 145.361, 142.445,
             142.442, 142.428, 146.388],
        'brightness' : [400, 10, 316.5, 150, 500, 312.6, 312.7, 324.4, 373.6,
             359.6, 312.9, 100, 400, 500, 300, 250, 100, 150, 300, 400,
             250, 300, 332, 450, 200, 150, 400, 100],
        'acq_date' : ['2008-03-08', '2008-03-08', '2006-01-24', '2006-01-24', '2006-01-24', '2006-01-24', '2006-01-24',
             '2006-01-24', '2006-01-24', '2006-01-24', '2006-01-24', '2006-01-25', '2006-01-25',
             '2006-01-28', '2006-01-28', '2006-01-30', '2006-03-06', '2006-03-06', '2006-03-06',
             '2006-03-06', '2007-01-24', '2007-01-24', '2007-01-24', '2007-01-24', '2007-01-24',
             '2008-03-08', '2008-03-08', '2008-03-08']}

        firms, description = TestReaderDF._read_firms_synth(firms)

        self.assertEqual(firms['latitude'][0], -38.104)
        self.assertEqual(firms['longitude'][0], 146.388)
        self.assertEqual(firms['latitude'].iloc[-1], -38.104)
        self.assertEqual(firms['longitude'].iloc[-1], 146.388)
        self.assertFalse(firms['datenum'][0] == firms['datenum'][9])

        firms = bf._firms_cons_days(firms)

        self.assertEqual(firms['cons_id'][0], 0)
        self.assertEqual(firms['cons_id'][7], 0)
        self.assertEqual(firms['cons_id'][8], 0)
        self.assertEqual(firms['cons_id'][9], 0)
        self.assertEqual(firms['cons_id'][10], 0)
        self.assertEqual(firms['cons_id'][11], 1)
        self.assertEqual(firms['cons_id'][13], 1)
        self.assertEqual(firms['cons_id'][15], 2)
        self.assertEqual(firms['cons_id'][21], 3)
        self.assertEqual(firms['cons_id'][26], 4)

        centroids, res_data = bf._centroids_creation(firms, 1)

        firms = bf._firms_clustering(firms, res_data)

        self.assertEqual(max((firms['clus_id'][:10]).values), 2)
        self.assertEqual(max((firms['clus_id'][11:13]).values), 0)

        firms = bf._firms_event(firms)

        self.assertEqual(max((firms['event_id'][:10]).values), 3)
        self.assertEqual(firms['event_id'][11], 4)
        self.assertEqual(firms['event_id'][12], 4)
        self.assertEqual(firms['event_id'][13], 5)

         # add brightness matrix
        bf._calc_brightness(firms, centroids)

        self.assertEqual(bf.intensity[0, 1172], 500)
        self.assertEqual(bf.intensity[0, 4714], 312.7)
        self.assertEqual(bf.intensity[0, 4717], 312.6)
        self.assertEqual(bf.intensity[1, 227620], 312.9)
        self.assertEqual(bf.intensity[2, 232658], 324.4)
        self.assertEqual(bf.intensity[2, 236200], 359.6)
        self.assertEqual(bf.intensity[2, 237385], 373.6)
        self.assertEqual(bf.intensity[3, 1172], 500)
        self.assertEqual(bf.intensity[3, 4717], 300)
        self.assertEqual(bf.intensity[4, 227620], 250)

        # add probabilistic event
        ev_id = 1
        bf._random_bushfire_one_event(ev_id, 1)

# Execute Tests
if __name__ == "__main__":
    TESTS = unittest.TestLoader().loadTestsFromTestCase(TestReaderDF)
    unittest.TextTestRunner(verbosity=2).run(TESTS)
