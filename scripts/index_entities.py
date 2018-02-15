from elasticsearch import Elasticsearch
from geo_admin.models import Department, Locality, Municipality,\
    Settlement, State


def run():
    try:
        es = Elasticsearch()
        index_states(es)
        index_departments(es)
        index_municipalities(es)
        index_localities(es)
        index_settlements(es)
    except Exception as e:
        print(e)


def index_states(es):
    if es.indices.exists(index='provincias'):
        print('-- Ya existe el índice de Provincias.')
        return
    print('-- Creando índice de Provincias.')

    mapping = {
        'provincia': {
            'properties': {
                'id': {'type': 'text'},
                'name': {'type': 'text'},
                'geometry': {'type': 'geo_shape'}
            }
        }
    }
    es.indices.create(index='provincias')
    es.indices.put_mapping(index='provincias', doc_type='provincia',
                           body=mapping)

    data = []
    for state in State.objects.all():
        data.append({'index': {'_id': state.id}})
        data.append({
            'id': state.code,
            'nombre': state.name,
            'geometry': {
                'type': 'polygon',
                'coordinates': state.geom.coords
            }
        })
    es.bulk(index='provincias', doc_type='provincia', body=data, refresh=True,
            request_timeout=320)

    print('-- Se creó el índice de Provincias exitosamente.')


def index_departments(es):
    if es.indices.exists(index='departamentos'):
        print('-- Ya existe el índice de Departamentos.')
        return
    print('-- Creando índice de Departamentos.')

    mapping = {
        'departamento': {
            'properties': {
                'id': {'type': 'text'},
                'name': {'type': 'text'},
                'geometry': {'type': 'geo_shape'},
                'provincia': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'text'},
                        'name': {'type': 'text'},
                    }
                }
            }
        }
    }
    es.indices.create(index='departamentos')
    es.indices.put_mapping(index='departamentos', doc_type='departamento',
                           body=mapping)

    data = []
    states = {state.id: (state.code, state.name) for state in State.objects.all()}
    for dept in Department.objects.all():
        geometry = {}
        if dept.geom is not None:
            geometry = {
                'type': 'polygon',
                'coordinates': dept.geom.coords,
            }
        data.append({'index': {'_id': dept.id}})
        data.append({
            'id': dept.code,
            'nombre': dept.name,
            'geometry': geometry,
            'provincia': {
                'id': states[dept.state_id][0],
                'nombre': states[dept.state_id][1]
            }
        })
    es.bulk(index='departamentos', doc_type='departamento', body=data,
            refresh=True, request_timeout=320)
    print('-- Se creó el índice de Departamentos exitosamente.')


def index_municipalities(es):
    if es.indices.exists(index='municipios'):
        print('-- Ya existe el índice de Municipios.')
        return
    print('-- Creando índice de Municipios.')

    mapping = {
        'municipio': {
            'properties': {
                'id': {'type': 'text'},
                'name': {'type': 'text'},
                'geometry': {'type': 'geo_shape'},
                'departamento': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'text'},
                        'name': {'type': 'text'},
                    }
                },
                'provincia': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'text'},
                        'name': {'type': 'text'},
                    }
                }
            }
        }
    }
    es.indices.create(index='municipios')
    es.indices.put_mapping(index='municipios', doc_type='municipio',
                           body=mapping)

    data = []
    states = {state.id: (state.code, state.name) for state in
              State.objects.all()}
    departments = {dept.id: (dept.code, dept.name) for dept in
                   Department.objects.all()}
    for mun in Municipality.objects.all():
        data.append({'index': {'_id': mun.id}})
        data.append({
            'id': mun.code,
            'nombre': mun.name,
            'departamento': {
                'id': departments[mun.department_id][0],
                'nombre': departments[mun.department_id][1]
            },
            'provincia': {
                'id': states[mun.state_id][0],
                'nombre': states[mun.state_id][1]
            },
            'geometry': {
                'type': 'polygon',
                'coordinates': mun.geom.coords,
            }
        })

    es.bulk(index='municipios', doc_type='municipio', body=data,
            refresh=True, request_timeout=320)
    print('-- Se creó el índice de Municipios exitosamente.')


def index_localities(es):
    if es.indices.exists(index='localidades'):
        print('-- Ya existe el índice de Localidades.')
        return
    print('-- Creando índice de Localidades.')
    data = []
    states = {state.id: (state.code, state.name) for state in State.objects.all()}
    departments = {dept.id: (dept.code, dept.name) for dept in Department.objects.all()}
    for locality in Locality.objects.all():
        data.append({'index': {'_id': locality.id}})
        data.append({
            'id': locality.code,
            'nombre': locality.name,
            'departamento': {
                'id': departments[locality.department_id][0],
                'nombre': departments[locality.department_id][1]
            },
            'provincia': {
                'id': states[locality.state_id][0],
                'nombre': states[locality.state_id][1]
            }
        })
    es.bulk(index='localidades', doc_type='localidad', body=data, refresh=True,
            request_timeout=120)
    print('-- Se creó el índice de Localidades exitosamente.')


def index_settlements(es):
    if es.indices.exists(index='bahra'):
        print('-- Ya existe el índice de BAHRA.')
        return
    print('-- Creando índice de Asentamientos.')

    mapping = {
        'asentamiento': {
            'properties': {
                'id': {'type': 'text'},
                'nombre': {'type': 'text'},
                'tipo': {'type': 'text'},
                'departamento': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'text'},
                        'name': {'type': 'text'},
                    }
                },
                'provincia': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'text'},
                        'name': {'type': 'text'},
                    }
                },
                'geometry': {'type': 'geo_shape'},
            }
        }
    }
    es.indices.create(index='bahra')
    es.indices.put_mapping(index='bahra', doc_type='asentamiento', body=mapping)

    barha_types = {
        'E': 'Entidad (E)',
        'LC': 'Componente de localidad compuesta (LC)',
        'LS': 'Localidad simple (LS)'
    }
    data = []
    states = {state.id: (state.code, state.name) for state in State.objects.all()}
    departments = {dept.id: (dept.code, dept.name) for dept in Department.objects.all()}
    for settlement in Settlement.objects.all():
        data.append({'index': {'_id': settlement.id}})
        data.append({
            'id': settlement.code,
            'nombre': settlement.name,
            'tipo': barha_types[settlement.bahra_type],
            'departamento': {
                'id': departments[settlement.department_id][0],
                'nombre': departments[settlement.department_id][1]
            },
            'provincia': {
                'id': states[settlement.state_id][0],
                'nombre': states[settlement.state_id][1]
            },
            'geometry': {
                'type': 'multipoint',
                'coordinates': settlement.geom.coords
            }
        })
    es.bulk(index='bahra', doc_type='asentamiento', body=data, refresh=True,
            request_timeout=320)
    print('-- Se creó el índice de Asentamientos exitosamente.')
