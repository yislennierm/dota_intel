from neo4j import GraphDatabase

URI = "bolt://localhost:55003"
AUTH = ("neo4j", "abcd1234")

driver = GraphDatabase.driver(URI, auth=AUTH)

def get_driver():
    return driver
