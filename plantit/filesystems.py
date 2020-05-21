from plantit.stores.irods import IRODS
from plantit.stores import registrar

registrar.register(IRODS(name = "irods",
                         username = "rods",
                         password = "rods",
                         port = 1247,
                         hostname = "irods",
                         zone = "tempZone"),
                    lambda user: "/tempZone/home/rods/")

