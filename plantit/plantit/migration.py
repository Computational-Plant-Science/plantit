import pymysql
from pymysql import MySQLError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit import settings


SELECT_MANAGED_FILE_BY_PATH =               """SELECT fid, filename, uri FROM file_managed WHERE uri LIKE %s"""
SELECT_MANAGED_FILE_BY_FID =                """SELECT fid, filename, uri FROM file_managed WHERE fid = %s"""
SELECT_ROOT_IMAGE =                         """SELECT entity_id FROM field_data_field_root_image WHERE field_root_image_fid = %s"""
SELECT_ROOT_COLLECTION =                    """SELECT entity_id FROM field_data_field_marked_coll_root_img_ref WHERE field_marked_coll_root_img_ref_target_id = %s"""
SELECT_ROOT_COLLECTION_TITLE =              """SELECT title, created, changed FROM node WHERE nid = %s"""
SELECT_ROOT_COLLECTION_METADATA =           """SELECT field_collection_metadata_first, field_collection_metadata_second FROM field_data_field_collection_metadata WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_LOCATION =           """SELECT field_collection_location_lat, field_collection_location_lng FROM field_data_field_collection_location WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_PLANTING =           """SELECT field_collection_plantation_value FROM field_data_field_collection_plantation WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_HARVEST =            """SELECT field_collection_harvest_value FROM field_data_field_collection_harvest WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_GROUP =         """SELECT field_collection_soil_group_tid FROM field_data_field_collection_soil_group WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_MOISTURE =      """SELECT field_collection_soil_moisture_value FROM field_data_field_collection_soil_moisture WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_N =             """SELECT field_collection_soil_nitrogen_value FROM field_data_field_collection_soil_nitrogen WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_P =             """SELECT field_collection_soil_phosphorus_value FROM field_data_field_collection_soil_phosphorus WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_SOIL_K =             """SELECT field_collection_soil_potassium_value FROM field_data_field_collection_soil_potassium WHERE entity_id = %s"""
SELECT_ROOT_COLLECTION_PESTICIDES =         """SELECT field_collection_pesticides_value FROM field_data_field_collection_pesticides WHERE entity_id = %s"""
SELECT_OUTPUT_FILE =                        """SELECT entity_id FROM field_data_field_exec_result_file WHERE field_exec_result_file_fid = %s"""
SELECT_OUTPUT_LOG_FILE =                    """SELECT entity_id FROM field_revision_field_output_log_file WHERE field_exec_result_file_fid = %s"""
SELECT_METADATA_FILE =                      """SELECT entity_id FROM field_data_field_metadata_file WHERE field_exec_result_file_fid = %s"""


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_managed_file_rows(username: str):
    db = pymysql.connect(host=settings.DIRT_MIGRATION_DB_HOST,
                         port=int(settings.DIRT_MIGRATION_DB_PORT),
                         user=settings.DIRT_MIGRATION_DB_USER,
                         db=settings.DIRT_MIGRATION_DB_DATABASE,
                         password=settings.DIRT_MIGRATION_DB_PASSWORD)
    cursor = db.cursor()
    storage_path = f"public://{username}/%"
    cursor.execute(SELECT_MANAGED_FILE_BY_PATH, (storage_path,))
    rows = cursor.fetchall()
    db.close()
    return rows


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_file_entity_row(file_id):
    db = pymysql.connect(host=settings.DIRT_MIGRATION_DB_HOST,
                         port=int(settings.DIRT_MIGRATION_DB_PORT),
                         user=settings.DIRT_MIGRATION_DB_USER,
                         db=settings.DIRT_MIGRATION_DB_DATABASE,
                         password=settings.DIRT_MIGRATION_DB_PASSWORD)
    cursor = db.cursor()
    cursor.execute(SELECT_ROOT_IMAGE, (file_id,))
    row = cursor.fetchone()
    db.close()
    return row


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_collection_entity_id_row(file_entity_id):
    db = pymysql.connect(host=settings.DIRT_MIGRATION_DB_HOST,
                         port=int(settings.DIRT_MIGRATION_DB_PORT),
                         user=settings.DIRT_MIGRATION_DB_USER,
                         db=settings.DIRT_MIGRATION_DB_DATABASE,
                         password=settings.DIRT_MIGRATION_DB_PASSWORD)
    cursor = db.cursor()
    cursor.execute(SELECT_ROOT_COLLECTION, (file_entity_id,))
    row = cursor.fetchone()
    db.close()
    return row


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_marked_collection_row(coll_entity_id):
    db = pymysql.connect(host=settings.DIRT_MIGRATION_DB_HOST,
                         port=int(settings.DIRT_MIGRATION_DB_PORT),
                         user=settings.DIRT_MIGRATION_DB_USER,
                         db=settings.DIRT_MIGRATION_DB_DATABASE,
                         password=settings.DIRT_MIGRATION_DB_PASSWORD)
    cursor = db.cursor()
    cursor.execute(SELECT_ROOT_COLLECTION_TITLE, (coll_entity_id,))
    row = cursor.fetchone()
    db.close()
    return row


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(MySQLError)))
def get_marked_collection_data_rows(coll_entity_id):
    db = pymysql.connect(host=settings.DIRT_MIGRATION_DB_HOST,
                         port=int(settings.DIRT_MIGRATION_DB_PORT),
                         user=settings.DIRT_MIGRATION_DB_USER,
                         db=settings.DIRT_MIGRATION_DB_DATABASE,
                         password=settings.DIRT_MIGRATION_DB_PASSWORD)
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
    db.close()

    return metadata_rows, location_row, planting_row, harvest_row, soil_group_row, soil_moist_row, soil_n_row, soil_p_row, soil_k_row, pesticides_row
