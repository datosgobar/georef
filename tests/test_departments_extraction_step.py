from georef_ar_etl.provinces import ProvincesExtractionStep
from georef_ar_etl.departments import DepartmentsExtractionStep
from . import ETLTestCase

SANTA_FE_DEPT_COUNT = 19


class TestDepartmentsExtractionStep(ETLTestCase):
    def setUp(self):
        super().setUp()
        self._tmp_provinces = self.create_test_provinces()
        self._tmp_departments = self.create_test_departments()

        step = ProvincesExtractionStep()
        step.run(self._tmp_provinces, self._ctx)

    def tearDown(self):
        self._ctx.session.commit()
        self._ctx.session.query(self._tmp_departments).delete()
        self._ctx.session.query(self._tmp_provinces).delete()
        super().tearDown()

    def test_single(self):
        """Los departamentos deberían poder ser procesados desde la tabla
        tmp_departamentos e insertados en la tabla correspondiente
        georef_departamentos."""
        step = DepartmentsExtractionStep()
        departments = step.run(self._tmp_departments, self._ctx)

        # Santa Fe tiene 19 departamentos
        self.assertEqual(self._ctx.session.query(departments).count(),
                         SANTA_FE_DEPT_COUNT)

        report_data = self._ctx.report.get_data('departments_extraction')
        self.assertEqual(len(report_data['new_entities_ids']),
                         SANTA_FE_DEPT_COUNT)

    def test_field_change(self):
        """Si se modifica un campo de un departamento (no el ID), luego de la
        extracción el campo nuevo debería figurar en georef_departamentos."""
        # Ejecutar la extracción por primera vez
        step = DepartmentsExtractionStep()
        step.run(self._tmp_departments, self._ctx)

        self._ctx.session.query(self._tmp_departments).\
            filter_by(in1='82077').\
            update({'nam': '8 de Julio'})

        departments = step.run(self._tmp_departments, self._ctx)
        name = self._ctx.session.query(departments).\
            filter_by(id='82077').\
            one().nombre
        self.assertEqual(name, '8 de Julio')

    def test_clean_string(self):
        """Los campos de texto deberían ser normalizados en el proceso de
        normalización."""
        self._ctx.session.query(self._tmp_departments).\
            filter_by(in1='82077').\
            update({'nam': '  8 de Julio\n\n9 de Julio'})

        step = DepartmentsExtractionStep()
        departments = step.run(self._tmp_departments, self._ctx)
        name = self._ctx.session.query(departments).\
            filter_by(id='82077').\
            one().nombre
        self.assertEqual(name, '8 de Julio')

    def test_invalid_province(self):
        """Si un departamento hace referencia a una provincia inexistente, se
        debería reportar el error."""
        new_id = '83077'
        self._ctx.session.query(self._tmp_departments).\
            filter_by(in1='82077').\
            update({'in1': new_id})

        step = DepartmentsExtractionStep()
        departments = step.run(self._tmp_departments, self._ctx)
        query = self._ctx.session.query(departments).filter_by(id=new_id)
        self.assertEqual(query.count(), 0)

        report_data = self._ctx.report.get_data('departments_extraction')
        self.assertEqual(len(report_data['error_count']), 1)
        self.assertEqual(len(report_data['new_entities_ids']),
                         SANTA_FE_DEPT_COUNT - 1)
