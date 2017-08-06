from . import APITestCase
from api import actions
import json

from shapely import wkt, wkb

class TestPut(APITestCase):

    def setUp(self):
        structure_data = {
            "constraints": [
                {
                    "constraint_type": "PRIMARY KEY",
                    "constraint_parameter": "id",
                    "reference_table": None,
                    "reference_column": None
                }
            ],
            "columns": [
                {
                    "name": "id",
                    "data_type": "integer",
                    "is_nullable": False,
                    "character_maximum_length": None
                },
                {
                    "name": "name",
                    "data_type": "character varying",
                    "is_nullable": True,
                    "character_maximum_length": 50
                }, {
                    "name": "address",
                    "data_type": "character varying",
                    "is_nullable": True,
                    "character_maximum_length": 150
                }, {
                    "name": "geom",
                    "data_type": "Geometry (Point)",
                    "is_nullable": True,
                }
            ]
        }

        c_basic_resp = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': structure_data}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        assert c_basic_resp.status_code==201, c_basic_resp.json().get('reason','No reason returned')

    def tearDown(self):
        meta_schema = actions.get_meta_schema_name(self.test_schema)
        if actions.has_table(
                dict(table=self.test_table, schema=self.test_schema)):
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_insert_table_name(self.test_schema,
                                                        self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_edit_table_name(self.test_schema,
                                                      self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_delete_table_name(self.test_schema,
                                                        self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=self.test_schema,
                    table=self.test_table
                ))

    def test_put_with_id(self):
        row = {'id': 1, 'name': 'John Doe', 'address': None}
        response = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': row}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 201, response.json().get('reason', 'No reason returned'))
        row['geom'] = None
        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json())

        self.assertDictEqualKeywise(response.json(), row)

    def test_put_with_wrong_id(self):
        response = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': {'id': 2, 'name': 'John Doe',
                                       'address': None}}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 409, response.json().get('reason', 'No reason returned'))

    def test_put_with_existing_id(self):
        self.test_put_with_id()

        another_row = {'id': 1, 'name': 'Mary Doe', 'address': "Mary's Street"}

        response = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': another_row}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 200, response.json().get('reason', 'No reason returned'))

        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason', 'No reason returned'))

        another_row['geom'] = None

        self.assertDictEqualKeywise(response.json(), another_row)

    def test_put_geometry(self):
        row = {'id': 1, 'name': 'Mary Doe', 'address': "Mary's Street", 'geom': 'POINT(-71.160281 42.258729)'}

        response = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': row}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 201, response.json().get('reason', 'No reason returned'))

        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason', 'No reason returned'))

        row['geom'] = wkb.dumps(wkt.loads(row['geom']), hex=True)
        self.assertDictEqualKeywise(response.json(), row)

    def test_put_geometry_wtb(self):
        row = {'id': 1, 'name': 'Mary Doe', 'address': "Mary's Street",
               'geom':  wkb.dumps(wkt.loads('POINT(-71.160281 42.258729)'), hex=True)}

        response = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': row}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 201,
                         response.json().get('reason',
                                             'No reason returned'))

        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason',
                                             'No reason returned'))

        self.assertDictEqualKeywise(response.json(), row)


class TestPost(APITestCase):
    def setUp(self):
        self.rows = [{'id': 1, 'name': 'John Doe', 'address': None, 'geom': 'Point(-71.160281 42.258729)'}]
        self.test_table = 'test_table_rows'
        self.test_schema = 'test'
        structure_data = {
            "constraints": [
                {
                    "constraint_type": "PRIMARY KEY",
                    "constraint_parameter": "id",
                    "reference_table": None,
                    "reference_column": None
                }
            ],
            "columns": [
                {
                    "name": "id",
                    "data_type": "integer",
                    "is_nullable": False,
                    "character_maximum_length": None
                },
                {
                    "name": "name",
                    "data_type": "character varying",
                    "is_nullable": True,
                    "character_maximum_length": 50
                }, {
                    "name": "address",
                    "data_type": "character varying",
                    "is_nullable": True,
                    "character_maximum_length": 150
                }, {
                    "name": "geom",
                    "data_type": "geometry (point)",
                    "is_nullable": True,
                }
            ]
        }

        c_basic_resp = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': structure_data}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        assert c_basic_resp.status_code==201, 'Returned %d: %s'%(c_basic_resp.status_code, c_basic_resp.json().get('reason','No reason returned'))

    def tearDown(self):
        meta_schema = actions.get_meta_schema_name(self.test_schema)
        if actions.has_table(
                dict(table=self.test_table, schema=self.test_schema)):
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_insert_table_name(self.test_schema,
                                                        self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_edit_table_name(self.test_schema,
                                                      self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_delete_table_name(self.test_schema,
                                                        self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=self.test_schema,
                    table=self.test_table
                ))

    def test_simple_post_new(self, rid=1):
        row = {'id': rid, 'name': 'Mary Doe', 'address': "Mary's Street",
               'geom':'POINT(-71.160281 42.258729)'}

        response = self.__class__.client.post(
            '/api/v0/schema/{schema}/tables/{table}/rows/new'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': row}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 201,
                         response.json().get('reason', 'No reason returned'))

        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/{rid}'.format(
                schema=self.test_schema, table=self.test_table, rid=rid))

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason', 'No reason returned'))

        row['geom'] = wkb.dumps(wkt.loads(row['geom']), hex=True)
        self.assertDictEqualKeywise(response.json(), row)

    def test_simple_post_existing(self):
        self.test_simple_post_new()
        self.test_simple_post_new(rid=2)
        row = {'id': 2, 'name': 'John Doe', 'address': "John's Street",
               'geom':'POINT(42.258729 -71.160281)'}

        response = self.__class__.client.post(
            '/api/v0/schema/{schema}/tables/{table}/rows/2'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': row}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason', 'No reason returned'))

        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/2'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason', 'No reason returned'))

        row['geom'] = wkb.dumps(wkt.loads(row['geom']), hex=True)
        self.assertDictEqualKeywise(response.json(), row)

        # Check whether other rows remained unchanged

        row = {'id': 1, 'name': 'Mary Doe', 'address': "Mary's Street",
               'geom': 'POINT(-71.160281 42.258729)'}

        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/1'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json().get('reason', 'No reason returned'))

        row['geom'] = wkb.dumps(wkt.loads(row['geom']), hex=True)
        self.assertDictEqualKeywise(response.json(), row)

class TestGet(APITestCase):
    def setUp(self):
        self.rows = [{'id': 1, 'name': 'John Doe', 'address': None, 'geom': 'Point(-71.160281 42.258729)'}]
        self.test_table = 'test_table_rows'
        structure_data = {
            "constraints": [
                {
                    "constraint_type": "PRIMARY KEY",
                    "constraint_parameter": "id",
                    "reference_table": None,
                    "reference_column": None
                }
            ],
            "columns": [
                {
                    "name": "id",
                    "data_type": "integer",
                    "is_nullable": False,
                    "character_maximum_length": None
                },
                {
                    "name": "name",
                    "data_type": "character varying",
                    "is_nullable": True,
                    "character_maximum_length": 50
                }, {
                    "name": "address",
                    "data_type": "character varying",
                    "is_nullable": True,
                    "character_maximum_length": 150
                }, {
                    "name": "geom",
                    "data_type": "geometry (point)",
                    "is_nullable": True,
                }
            ]
        }

        c_basic_resp = self.__class__.client.put(
            '/api/v0/schema/{schema}/tables/{table}/'.format(
                schema=self.test_schema, table=self.test_table),
            data=json.dumps({'query': structure_data}),
            HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
            content_type='application/json')

        assert c_basic_resp.status_code==201, c_basic_resp.json()

        self.rows = []

        for i in range(100):
            row = {'id': i, 'name': 'Mary Doe', 'address': "Mary's Street",
                   'geom': '0101000000E44A3D0B42CA51C06EC328081E214540'}

            response = self.__class__.client.put(
                '/api/v0/schema/{schema}/tables/{table}/rows/{rid}'.format(
                    schema=self.test_schema, table=self.test_table, rid=i),
                data=json.dumps({'query': row}),
                HTTP_AUTHORIZATION='Token %s' % self.__class__.token,
                content_type='application/json')

            assert c_basic_resp.status_code == 201, c_basic_resp.json().get(
                'reason', 'No reason returned')

            self.rows.append(row)

    def tearDown(self):
        meta_schema = actions.get_meta_schema_name(self.test_schema)
        if actions.has_table(
                dict(table=self.test_table, schema=self.test_schema)):
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_insert_table_name(self.test_schema,
                                                        self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_edit_table_name(self.test_schema,
                                                      self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=meta_schema,
                    table=actions.get_delete_table_name(self.test_schema,
                                                        self.test_table)
                ))
            actions.perform_sql(
                "DROP TABLE IF EXISTS {schema}.{table} CASCADE".format(
                    schema=self.test_schema,
                    table=self.test_table
                ))

    def test_simple_get(self):
        response = self.__class__.client.get(
            '/api/v0/schema/{schema}/tables/{table}/rows/'.format(
                schema=self.test_schema, table=self.test_table))

        self.assertEqual(response.status_code, 200,
                         response.json())

        for c in zip(response.json(), self.rows):
            self.assertDictEqualKeywise(*c)