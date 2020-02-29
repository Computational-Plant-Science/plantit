from plantit.file_manager.filesystems.irods import IRODS
from plantit.file_manager.filesystems import registrar

registrar.register(IRODS(name = "irods",
                         username = "rods",
                         password = "rods",
                         port = 1247,
                         hostname = "irods",
                         zone = "tempZone"),
                    lambda user: "/tempZone/home/rods/")
