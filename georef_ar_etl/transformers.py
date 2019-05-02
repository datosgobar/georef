import os
from abc import abstractmethod
from zipfile import ZipFile, BadZipFile
import tarfile
from .exceptions import ValidationException, ProcessException
from .process import Step
from . import utils


class ExtractZipStep(Step):
    def __init__(self, internal_path=''):
        super().__init__('extract_zip')
        self._internal_path = internal_path

    def _run_internal(self, filename, ctx):
        dirname = filename.split('.')[0]
        if ctx.fs.isdir(dirname):
            ctx.report.info('Zip: Removiendo directorio "%s" anterior.',
                            dirname)
            ctx.fs.removetree(dirname)

        dirpath = os.path.dirname(ctx.fs.getsyspath(filename))

        try:
            with ctx.fs.open(filename, 'rb') as f:
                with ZipFile(f) as zipf:
                    zipf.extractall(os.path.join(dirpath, dirname))
        except BadZipFile as e:
            raise ProcessException(
                'No se pudo extraer el archivo .zip: {}'.format(e))

        return os.path.join(dirname, self._internal_path)


class ExtractTarStep(Step):
    def __init__(self):
        super().__init__('extract_tar')

    def _run_internal(self, filename, ctx):
        dirname = filename.split('.')[0]
        if ctx.fs.isdir(dirname):
            ctx.report.info('Tar: Removiendo directorio "%s" anterior.',
                            dirname)
            ctx.fs.removetree(dirname)

        sys_filename = ctx.fs.getsyspath(filename)
        dirpath = os.path.dirname(sys_filename)

        try:
            with tarfile.open(sys_filename) as tarf:
                tarf.extractall(os.path.join(dirpath, dirname))
        except tarfile.ReadError as e:
            raise ProcessException(
                'No se pudo extraer el archivo .tar: {}'.format(e))

        return dirname


class EntitiesExtractionStep(Step):
    def __init__(self, name, entity_class, entity_class_pkey,
                 tmp_entity_class_pkey):
        super().__init__(name)
        self._entity_class = entity_class
        self._entity_class_pkey = entity_class_pkey
        self._tmp_entity_class_pkey = tmp_entity_class_pkey

    def _run_internal(self, tmp_entities, ctx):
        ctx.report.info('Comenzando extracción...')
        self._patch_tmp_entities(tmp_entities, ctx)

        entities = []
        bulk_size = ctx.config.getint('etl', 'bulk_size')
        query = self._build_entities_query(tmp_entities, ctx)
        count = self._entities_query_count(tmp_entities, ctx)
        cached_session = ctx.cached_session()
        deleted = []
        updated = set()
        added = set()
        errors = []

        if not count:
            raise ProcessException('No hay entidades a procesar.')

        ctx.report.info('Entidades a procesar: {}'.format(count))

        for tmp_entity in utils.pbar(query, ctx, total=count):
            entity_id = getattr(tmp_entity, self._tmp_entity_class_pkey)
            prev_entity = ctx.session.query(self._entity_class).get(entity_id)

            if entity_id in added or entity_id in updated:
                raise ProcessException(
                    'Clave primaria "{}" repetida,'
                    ' tabla: "{}", columna: "{}".'.format(
                        entity_id, tmp_entities.__table__.name,
                        self._tmp_entity_class_pkey))

            try:
                new_entity = self._process_entity(tmp_entity, cached_session,
                                                  ctx)
            except ValidationException as e:
                errors.append((entity_id, str(e)))
                continue

            if prev_entity:
                utils.update_entity(new_entity, prev_entity)
                updated.add(entity_id)
            else:
                entities.append(new_entity)
                added.add(entity_id)

            if len(entities) > bulk_size:
                # Insertar todas las entidades en la Session. La próxima vez
                # que se utilice query(), se llamará antes a flush() (por la
                # configuración autoflush=True). Por lo tanto, no es necesario
                # llamar a flush()+expunge_all() manualmente.
                ctx.session.add_all(entities)
                entities.clear()

        ctx.session.add_all(entities)

        ctx.report.info('Buscando entidades eliminadas...')

        query = ctx.session.query(self._entity_class).yield_per(bulk_size)
        for entity in utils.pbar(query, ctx, total=query.count()):
            entity_id = getattr(entity, self._entity_class_pkey)

            if entity_id not in updated and entity_id not in added:
                ctx.session.query(self._entity_class).\
                    filter(getattr(self._entity_class,
                                   self._entity_class_pkey) == entity_id).\
                    delete()
                deleted.append(entity_id)

        ctx.report.info('Entidades nuevas: %s', len(added))
        ctx.report.info('Entidades actualizadas: %s', len(updated))
        ctx.report.info('Entidades eliminadas: %s', len(deleted))

        if errors:
            ctx.report.warn('Errores: %s\n', len(errors))

        report_data = ctx.report.get_data(self.name)
        report_data['new_entities_ids'] = list(added)
        report_data['updated_entities_count'] = len(updated)
        report_data['deleted_entities_ids'] = deleted
        report_data['errors'] = errors

        return self._entity_class

    def _build_entities_query(self, tmp_entities, ctx):
        bulk_size = ctx.config.getint('etl', 'bulk_size')
        return ctx.session.query(tmp_entities).yield_per(bulk_size)

    def _entities_query_count(self, tmp_entities, ctx):
        return self._build_entities_query(tmp_entities, ctx).count()

    @abstractmethod
    def _process_entity(self, entity, cached_session, ctx):
        raise NotImplementedError()

    def _patch_tmp_entities(self, tmp_entities, ctx):
        # Implementación default: noop
        pass
