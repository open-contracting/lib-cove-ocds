import json
import jsonref
import requests
import csv
import functools

from cached_property import cached_property
from .tools import cached_get_request
from urllib.parse import urlparse
from collections import OrderedDict
from flattentool.schema import get_property_type_set


class SchemaJsonMixin():
    @cached_property
    def release_schema_str(self):
        if getattr(self, 'cache_schema', False):
            response = cached_get_request(self.release_schema_url)
        else:
            response = requests.get(self.release_schema_url)
        return response.text

    @cached_property
    def release_pkg_schema_str(self):
        uri_scheme = urlparse(self.release_pkg_schema_url).scheme
        if uri_scheme == 'http' or uri_scheme == 'https':
            if getattr(self, 'cache_schema', False):
                response = cached_get_request(self.release_pkg_schema_url)
            else:
                response = requests.get(self.release_pkg_schema_url)
            return response.text
        else:
            with open(self.release_pkg_schema_url) as fp:
                return fp.read()

    @property
    def _release_schema_obj(self):
        return json.loads(self.release_schema_str, object_pairs_hook=OrderedDict)

    @property
    def _release_pkg_schema_obj(self):
        return json.loads(self.release_pkg_schema_str)

    def deref_schema(self, schema_str):
        try:
            return _deref_schema(schema_str, self.schema_host)
        except jsonref.JsonRefError as e:
            self.json_deref_error = e.message
            return {}

    def get_release_schema_obj(self, deref=False):
        if deref:
            return self.deref_schema(self.release_schema_str)
        return self._release_schema_obj

    def get_release_pkg_schema_obj(self, deref=False):
        if deref:
            return self.deref_schema(self.release_pkg_schema_str)
        return self._release_pkg_schema_obj

    def get_release_pkg_schema_fields(self):
        return set(schema_dict_fields_generator(self.get_release_pkg_schema_obj(deref=True)))


def schema_dict_fields_generator(schema_dict):
    if 'properties' in schema_dict and isinstance(schema_dict['properties'], dict):
        for property_name, value in schema_dict['properties'].items():
            if 'oneOf' in value:
                property_schema_dicts = value['oneOf']
            else:
                property_schema_dicts = [value]
            for property_schema_dict in property_schema_dicts:
                if not isinstance(property_schema_dict, dict):
                    continue
                property_type_set = get_property_type_set(property_schema_dict)
                if 'object' in property_type_set:
                    for field in schema_dict_fields_generator(property_schema_dict):
                        yield '/' + property_name + field
                elif 'array' in property_type_set:
                    fields = schema_dict_fields_generator(property_schema_dict.get('items', {}))
                    for field in fields:
                        yield '/' + property_name + field
                yield '/' + property_name


def get_schema_codelist_paths(schema_obj, obj=None, current_path=(), codelist_paths=None, use_extensions=False):
    '''Get a dict of codelist paths including the filename and if they are open.

    codelist paths are given as tuples of tuples:
        {("path", "to", "codelist"): (filename, open?), ..}
    '''
    if codelist_paths is None:
        codelist_paths = {}

    if schema_obj:
        obj = schema_obj.get_release_pkg_schema_obj(deref=True, use_extensions=use_extensions)

    properties = obj.get('properties', {})
    if not isinstance(properties, dict):
        return codelist_paths
    for prop, value in properties.items():
        if current_path:
            path = current_path + (prop,)
        else:
            path = (prop,)

        if "codelist" in value and path not in codelist_paths:
            codelist_paths[path] = (value['codelist'], value.get('openCodelist', False))

        if value.get('type') == 'object':
            get_schema_codelist_paths(None, value, path, codelist_paths)
        elif value.get('type') == 'array' and value.get('items', {}).get('properties'):
            get_schema_codelist_paths(None, value['items'], path, codelist_paths)

    return codelist_paths


def load_codelist(url):
    codelist_map = {}

    response = requests.get(url)
    response.raise_for_status()
    reader = csv.DictReader(line.decode("utf8") for line in response.iter_lines())
    for record in reader:
        code = record.get('Code') or record.get('code')
        title = record.get('Title') or record.get('Title_en')
        if not code:
            return {}
        codelist_map[code] = title

    return codelist_map


@functools.lru_cache()
def load_core_codelists(codelist_url, unique_files):
    codelists = {}
    for codelist_file in unique_files:
        try:
            codelist_map = load_codelist(codelist_url + codelist_file)
        except requests.exceptions.RequestException:
            return {}
        codelists[codelist_file] = codelist_map
    return codelists


@functools.lru_cache()
def _deref_schema(schema_str, schema_host):
    loader = CustomJsonrefLoader(schema_url=schema_host)
    deref_obj = jsonref.loads(schema_str, loader=loader, object_pairs_hook=OrderedDict)
    # Force evaluation of jsonref.loads here
    repr(deref_obj)
    return deref_obj


class CustomJsonrefLoader(jsonref.JsonLoader):
    '''This ref loader is only for use with the jsonref library
    and NOT jsonschema.'''
    def __init__(self, **kwargs):
        self.schema_url = kwargs.pop('schema_url', None)
        super().__init__(**kwargs)

    def get_remote_json(self, uri, **kwargs):
        # ignore url in ref apart from last part
        uri = self.schema_url + uri.split('/')[-1]
        if uri[:4] == 'http':
            return super().get_remote_json(uri, **kwargs)
        else:
            with open(uri) as schema_file:
                return json.load(schema_file, **kwargs)
