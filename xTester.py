import unittest

def parseExperimentType(experiment):
    if experiment == 'LUX-ZEPLIN' or experiment == 'LUX':
        dataset_type = 'DD'
        names = ['m_DM', 'sigma']
    else:
        dataset_type = 'LHC'
        names = ['m_med', 'm_DM']
    return dataset_type, names


class TestExperiment(unittest.TestCase):

    def test_workingExample(self):
        dataType, names = parseExperimentType('LUX')
        self.assertEqual(dataType,'DD')
        self.assertEqual(names,['m_DM', 'sigma'])

    def test_failingExample(self):
        dataType, names = parseExperimentType('IceCube')
        self.assertEqual(dataType,'DD')
        self.assertEqual(names,['m_DM', 'sigma'])

    def test_badExperimentType(self):
        dataType, names = parseExperimentType('this is a bad experiment string')
        self.assertNotEqual(dataType,'DD')
        self.assertNotEqual(dataType,'LHC')

if __name__ == '__main__':
    unittest.main()
