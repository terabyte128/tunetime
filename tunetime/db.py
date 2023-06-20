from tinydb import TinyDB, Query


db = TinyDB("db.json")

UserTable = db.table("users")
SessionTable = db.table("sessions")
