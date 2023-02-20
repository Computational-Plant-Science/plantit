from datetime import datetime
from typing import List, Tuple, NamedTuple, Optional

import pymysql
from pymysql import MySQLError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

import plantit.queries as q
import plantit.users.models
from plantit.ssh import SSH
from plantit import settings
from plantit.users.models import Profile, Migration, ManagedFile

SELECT_DIRT_CAS_USER = """SELECT * FROM cas_user WHERE cas_name = %s"""
SELECT_DIRT_USER = """SELECT * FROM users WHERE mail = %s"""
SELECT_MANAGED_FILE_BY_PATH = """SELECT fid, filename, uri FROM file_managed WHERE uri LIKE %s"""
SELECT_MANAGED_FILE_BY_FID = """SELECT fid, filename, uri FROM file_managed WHERE fid = %s"""
SELECT_ROOT_IMAGE = """SELECT entity_id FROM field_data_field_root_image WHERE field_root_image_fid = %s"""
SELECT_ROOT_COLLECTION = """SELECT entity_id FROM field_data_field_marked_coll_root_img_ref WHERE field_marked_coll_root_img_ref_target_id = %s"""
SELECT_ROOT_COLLECTION_TITLE = """SELECT title, created, changed FROM node WHERE nid = %s"""
SELECT_ROOT_COLLECTION_METADATA = """SELECT field_collection_metadata_first, field_collection_metadata_second FROM field_data_field_collection_metadata WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_LOCATION = """SELECT field_collection_location_lat, field_collection_location_lng FROM field_data_field_collection_location WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_PLANTING = """SELECT field_collection_plantation_value FROM field_data_field_collection_plantation WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_HARVEST = """SELECT field_collection_harvest_value FROM field_data_field_collection_harvest WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_GROUP = """SELECT field_collection_soil_group_tid FROM field_data_field_collection_soil_group WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_MOISTURE = """SELECT field_collection_soil_moisture_value FROM field_data_field_collection_soil_moisture WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_N = """SELECT field_collection_soil_nitrogen_value FROM field_data_field_collection_soil_nitrogen WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_P = """SELECT field_collection_soil_phosphorus_value FROM field_data_field_collection_soil_phosphorus WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_K = """SELECT field_collection_soil_potassium_value FROM field_data_field_collection_soil_potassium WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_PESTICIDES = """SELECT field_collection_pesticides_value FROM field_data_field_collection_pesticides WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_METADATA = """SELECT field_root_image_metadata_first, field_root_image_metadata_second FROM field_data_field_root_image_metadata WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_RESOLUTION = """SELECT field_root_image_resolution_value FROM field_data_field_root_image_resolution WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_AGE = """SELECT field_root_img_age_value FROM field_data_field_root_img_age WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_DRY_BIOMASS = """SELECT field_root_img_dry_biomass_value FROM field_data_field_root_img_dry_biomass WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_FRESH_BIOMASS = """SELECT field_root_img_fresh_biomass_value FROM field_data_field_root_img_fresh_biomass WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_FAMILY = """SELECT field_root_img_family_value FROM field_data_field_root_img_family WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_GENUS = """SELECT field_root_img_genus_value FROM field_data_field_root_img_genus WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_SPAD = """SELECT field_root_img_spad_value FROM field_data_field_root_img_spad WHERE entity_id = %s"""
SELECT_ROOT_IMAGE_SPECIES = """SELECT field_root_img_species_value FROM field_data_field_root_img_species WHERE entity_id = %s"""
SELECT_OUTPUT_FILE = """SELECT entity_id FROM field_data_field_exec_result_file WHERE field_exec_result_file_fid = %s"""
SELECT_OUTPUT_LOG_FILE = """SELECT entity_id FROM field_revision_field_output_log_file WHERE field_exec_result_file_fid = %s"""
SELECT_METADATA_FILE = """SELECT entity_id FROM field_data_field_metadata_file WHERE field_exec_result_file_fid = %s"""


def get_db_connection():
    return pymysql.connect(host=settings.DIRT_MIGRATION_DB_HOST,
                           port=int(settings.DIRT_MIGRATION_DB_PORT),
                           user=settings.DIRT_MIGRATION_DB_USER,
                           db=settings.DIRT_MIGRATION_DB_DATABASE,
                           password=settings.DIRT_MIGRATION_DB_PASSWORD)


async def push_migration_event(
        user: User,
        migration: Migration,
        collection: str = None,
        file: ManagedFile = None,
        message: str = None):
    data = {
        'type': 'migration_event',
        'migration': q.migration_to_dict(migration),
    }
    if collection is not None: data['collection'] = collection
    if file is not None: data['file'] = q.managed_file_to_dict(file)
    if message is not None: data['message'] = message
    await get_channel_layer().group_send(f"{user.username}", data)


class MgdFile(NamedTuple):
    id: str
    name: str
    path: str
    type: str
    folder: str
    orphan: bool
    missing: bool
    uploaded: Optional[str]
    nfs_path: Optional[str] = None
    entity_id: Optional[str] = None
    collection: Optional[str] = None
    collection_entity_id: Optional[str] = None
    collection_datastore_id: Optional[str] = None


def row_to_managed_file(row):
    fid = row[0]
    name = row[1]
    path = row[2]

    if 'root-images' in path:
        return MgdFile(
            id=fid,
            name=name,
            path=path.replace('public://', ''),
            type='image',
            folder=path.rpartition('root-images')[2].replace(name, '').replace('/', ''),
            orphan=False,
            missing=False,
            uploaded=None)
    elif 'metadata-files' in path:
        return MgdFile(
            id=fid,
            name=name,
            path=path.replace('public://', ''),
            type='metadata',
            folder=path.rpartition('metadata-files')[2].replace(name, '').replace('/', ''),
            orphan=False,
            missing=False,
            uploaded=None)
    elif 'output-files' in path or 'output-images' in path:
        folder = path.rpartition('output-files' if 'output-files' in path else 'output-images')[2].replace(name, '').replace('/', '')
        return MgdFile(
            id=fid,
            name=name,
            path=path.replace('public://', ''),
            type='output',
            folder=folder,
            orphan=False,
            missing=False,
            uploaded=None)
    elif 'output-logs' in path:
        return MgdFile(
            id=fid,
            name=name,
            path=path.replace('public://', ''),
            type='logs',
            folder=path.rpartition('output-logs')[2].replace(name, '').replace('/', ''),
            orphan=False,
            missing=False,
            uploaded=None)
    else:
        raise ValueError(f"Unrecognized managed file type (path: {path})")


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_dirt_username(username: str, email: Optional[str]) -> Optional[str]:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        cursor.execute(SELECT_DIRT_CAS_USER, (username,))
        row = cursor.fetchone()
        if row is not None: return row[2]
        if email is not None:
            cursor.execute(SELECT_DIRT_USER, (email,))
            row = cursor.fetchone()
            return row['name'] if row is not None else None
        else:
            return None
    finally:
        db.close()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_managed_files(username: str) -> List[MgdFile]:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        storage_path = f"public://{username}/%"
        cursor.execute(SELECT_MANAGED_FILE_BY_PATH, (storage_path,))
        rows = cursor.fetchall()
        files = [row_to_managed_file(row) for row in rows]
        return [f for f in files if f is not None]
    finally:
        db.close()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_file_entity_id(file_id) -> str:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        cursor.execute(SELECT_ROOT_IMAGE, (file_id,))
        row = cursor.fetchone()
        return row[0] if row is not None else None
    finally:
        db.close()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_collection_entity_id(file_entity_id) -> str:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        cursor.execute(SELECT_ROOT_COLLECTION, (file_entity_id,))
        row = cursor.fetchone()
        return row[0] if row is not None else None
    finally:
        db.close()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_marked_collection(coll_entity_id) -> Tuple[str, datetime, datetime]:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        cursor.execute(SELECT_ROOT_COLLECTION_TITLE, (coll_entity_id,))
        row = cursor.fetchone()
        return (row[0], datetime.fromtimestamp(int(row[1])), datetime.fromtimestamp(int(row[2]))) if row is not None else None
    finally:
        db.close()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_marked_collection_info(coll_entity_id) -> Tuple[dict, float, float, str, str, str, float, float, float, float, str]:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        cursor.execute(SELECT_ROOT_COLLECTION_METADATA, (coll_entity_id,))
        metadata_rows = cursor.fetchall()
        cursor.execute(SELECT_ROOT_COLLECTION_LOCATION, (coll_entity_id,))
        location_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_PLANTING, (coll_entity_id,))
        planting_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_HARVEST, (coll_entity_id,))
        harvest_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_SOIL_GROUP, (coll_entity_id,))
        soil_group_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_SOIL_MOISTURE, (coll_entity_id,))
        soil_moist_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_SOIL_N, (coll_entity_id,))
        soil_n_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_SOIL_P, (coll_entity_id,))
        soil_p_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_SOIL_K, (coll_entity_id,))
        soil_k_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_COLLECTION_PESTICIDES, (coll_entity_id,))
        pesticides_row = cursor.fetchone()

        metadata = {row[0]: row[1] for row in metadata_rows}
        latitude = None if location_row is None else float(location_row[0])
        longitude = None if location_row is None else float(location_row[1])
        planting = None if planting_row is None else planting_row[0]
        harvest = None if harvest_row is None else harvest_row[0]
        soil_group = None if soil_group_row is None else soil_group_row[0]
        soil_moist = None if soil_moist_row is None else float(soil_moist_row[0])
        soil_n = None if soil_n_row is None else float(soil_n_row[0])
        soil_p = None if soil_p_row is None else float(soil_p_row[0])
        soil_k = None if soil_k_row is None else float(soil_k_row[0])
        pesticides = None if pesticides_row is None else pesticides_row[0]

        return metadata, latitude, longitude, planting, harvest, soil_group, soil_moist, soil_n, soil_p, soil_k, pesticides
    finally:
        db.close()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_root_image_info(image_entity_id) -> Tuple[dict, int, int, float, float, str, str, str, str]:
    db = get_db_connection()

    try:
        cursor = db.cursor()
        cursor.execute(SELECT_ROOT_IMAGE_METADATA, (image_entity_id,))
        metadata_rows = cursor.fetchall()
        cursor.execute(SELECT_ROOT_IMAGE_RESOLUTION, (image_entity_id,))
        resolution_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_AGE, (image_entity_id,))
        age_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_DRY_BIOMASS, (image_entity_id,))
        dry_biomass_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_FRESH_BIOMASS, (image_entity_id,))
        fresh_biomass_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_FAMILY, (image_entity_id,))
        family_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_GENUS, (image_entity_id,))
        genus_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_SPAD, (image_entity_id,))
        spad_row = cursor.fetchone()
        cursor.execute(SELECT_ROOT_IMAGE_SPECIES, (image_entity_id,))
        species_row = cursor.fetchone()

        metadata = {row[0]: row[1] for row in metadata_rows}
        resolution = None if resolution_row is None else int(resolution_row[0])
        age = None if age_row is None else int(age_row[0])
        dry_biomass = None if dry_biomass_row is None else float(dry_biomass_row[0])
        fresh_biomass = None if fresh_biomass_row is None else float(fresh_biomass_row[0])
        family = None if family_row is None else family_row[0]
        genus = None if genus_row is None else genus_row[0]
        spad = None if spad_row is None else spad_row[0]
        species = None if species_row is None else species_row[0]

        return metadata, resolution, age, dry_biomass, fresh_biomass, family, genus, spad, species
    finally:
        db.close()
