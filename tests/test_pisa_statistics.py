import unittest
import numpy as np
import pandas as pd
from test_pisa_2025 import load_module

a = load_module('spain_cycle_change', 'Global/pisa/analysis/spain_cycle_change.py')


class PISAStatisticsTests(unittest.TestCase):
    def test_weighted_mean_and_constant_replicates(self):
        y = np.array([100., 200.])
        w = np.tile(np.array([1., 3.])[:, None], (1, 81))
        point, se = a.summarize(a.mean_draws(y, w))
        self.assertEqual(point, 175.)
        self.assertEqual(se, 0.)

    def test_fay_and_imputation_variance(self):
        draws = np.tile(np.arange(10.)[None, :], (81, 1))
        draws[1:] += 2
        point, se = a.summarize(draws)
        self.assertEqual(point, 4.5)
        self.assertAlmostEqual(se**2, 16 + 1.1*np.var(np.arange(10.), ddof=1))

    def test_invalid_replicates_fail(self):
        with self.assertRaises(ValueError):
            a.mean_draws(np.array([1.]), np.zeros((1,81)))

    def test_education_code_shift(self):
        base = {'ST004D01T':[1,2,1], 'IMMIG':[1,2,3], 'REGION':[72401]*3,
                'STRATUM':['x']*3, 'ESCS':[-1,0,1], 'W_FSTUWT':[1.,1.,1.]}
        f22 = a.prepare(pd.DataFrame(base | {'HISCED':[3,6,7]}),2022,{'value_labels':{}})
        f25 = a.prepare(pd.DataFrame(base | {'HISCED':[2,5,6]}),2025,{'value_labels':{}})
        self.assertEqual(f22.educacion_familiar.tolist(), f25.educacion_familiar.tolist())

    def test_conflicting_duplicate_fails(self):
        import polars as pl
        m = load_module('merge_cycles_test','Global/pisa/pipelines/merge_trend_cycles.py')
        f = pl.DataFrame({'pisa_year':[2022]*2,'country':['ESP']*2,
                          'school_id':['1']*2,'student_id':['1']*2,'score':[1,2]})
        with self.assertRaises(ValueError): m.deduplicate_students(f)

    def test_region_uses_labels_not_changed_codes(self):
        base = {'ST004D01T':[1,2,1], 'IMMIG':[1,2,3], 'REGION':[72405]*3,
                'STRATUM':['x']*3,'ESCS':[-1,0,1],'W_FSTUWT':[1.,1.,1.],'HISCED':[1,2,3]}
        f = pd.DataFrame(base)
        a22 = a.prepare(f,2022,{'value_labels':{'REGION':{'72405.0':'Spain: Canary Islands'}}})
        a25 = a.prepare(f,2025,{'value_labels':{'REGION':{'72405':'Spain: Basque Country'}}})
        self.assertEqual(a22.region.iloc[0], 'Canary Islands')
        self.assertEqual(a25.region.iloc[0], 'Basque Country')

    def test_2025_male_indicator_fallback(self):
        f=pd.DataFrame({'ST004D01T':[np.nan,np.nan], 'MALE':[0,1],
                        'IMMIG':[1,2], 'REGION':[72401]*2, 'STRATUM':['x']*2,
                        'ESCS':[-1,1], 'W_FSTUWT':[1.,1.], 'HISCED':[2,6]})
        out=a.prepare(f,2025,{'value_labels':{}})
        self.assertEqual(out.sexo.tolist(),['No varón','Varón'])

    def test_suppressed_school_ids_require_unique_students(self):
        import polars as pl
        m = load_module('merge_suppressed','Global/pisa/pipelines/merge_trend_cycles.py')
        f = pl.DataFrame({'pisa_year':[2025]*2,'country':['LUX']*2,
                         'school_id':[None,None],'student_id':['1','2']})
        self.assertEqual(m.deduplicate_students(f)[0].height,2)

    def test_composition_decomposition_reconciles(self):
        frames = {}
        for year, sizes, means in [(2022,[100,100],[400,500]),(2025,[100,200],[390,480])]:
            f = pd.DataFrame({'group':np.repeat(['A','B'],sizes)})
            for w in a.WEIGHTS: f[w] = 1.
            for i in range(1,11): f[f'PV{i}MATH'] = np.repeat(means,sizes)
            frames[year] = f
        rows = a.decomposition(frames,('group',),'MATH')
        self.assertAlmostEqual(sum(r['composition']+r['within'] for r in rows),0.)
        self.assertGreater(sum(r['composition'] for r in rows),0.)
        self.assertLess(sum(r['within'] for r in rows),0.)


if __name__ == '__main__': unittest.main()
