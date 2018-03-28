import unittest
import os
from glob import glob
import untangle

dd_exp_list = ['lux', 'zeplin', 'xenon', 'icecube', 'pico', 'crest', 'darkside', 'cdms', 'panda']
collider_exp_list = ['lhc', 'atlas', 'cms']

def parseExperimentType(experiment):
    dataset_type, names = '',''
    if any(exp in experiment.lower() for exp in dd_exp_list):
            dataset_type = 'DD'
            names = ['m_DM', 'sigma']
    elif any(exp in experiment.lower() for exp in collider_exp_list):
            dataset_type = 'LHC'
            names = ['m_med', 'm_DM']
    else:
        raise ValueError('Unknown Experiment.')
    return dataset_type, names

def printAllExperiments():
    datasets = glob('data/*.xml')
    for dataset in datasets:
        metadata = untangle.parse(dataset)
        experiment = metadata.limit.experiment.cdata
        print experiment

class TestExperiment(unittest.TestCase):

    def test_DDExample(self):
        dataType, names = parseExperimentType('LUX')
        self.assertEqual(dataType,'DD')
        self.assertEqual(names,['m_DM', 'sigma'])

    def test_LHCExample(self):
        dataType, names = parseExperimentType('Atlas')
        self.assertEqual(dataType,'LHC')
        self.assertEqual(names,['m_med', 'm_DM'])

    def test_IceCubeExample(self):
        dataType, names = parseExperimentType('IceCube')
        self.assertEqual(dataType,'DD')
        self.assertEqual(names,['m_DM', 'sigma'])

    def test_badExperimentType(self):
        with self.assertRaises(Exception) as context:
            parseExperimentType('this is a bad experiment string')

        self.assertTrue('Unknown Experiment.' in context.exception)

    def test_XenonMatching(self):
        dataType, names = parseExperimentType('XENON1T')
        self.assertEqual(dataType,'DD')
        self.assertEqual(names,['m_DM', 'sigma'])

if __name__ == '__main__':
    unittest.main()
