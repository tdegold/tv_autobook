import sqlite3
from pprint import pprint

def clean_dump(file: str, write_to_file="") -> str:
    """Returns the content of a SQL-dump file but removes parts sqlite cannot correctly interpret
    
    :param file: path to the SQL-dump file
    :param write_to_file: if path to a file is provided, output text will also be written to that file
    :return: the sqlite-friendly content of the SQL-dump file
    """
    text = None
    with open(file, mode="r", encoding="utf-8") as sql_file:
        # need to replace some strings which sqlite cannot handle 
        # and which are not needed for our use case
        text = sql_file.read().replace(
            "SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";", ""
        ).replace(
            "START TRANSACTION;", ""
        ).replace(
            "SET time_zone = \"+00:00\";", ""
        ).replace("`", "").replace(
            " ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci", ""
        ).replace(
            " COLLATE utf8_unicode_ci", ""
        ).replace(
            " CHARACTER SET utf8", ""
        ).replace(
            "set('Herr','Frau')", "varchar(32)" # sets are not supportet in sqlite
        ).replace(
            "\\\'", "" # nasty strings within the "notiz"-field that mess up escaped characters
        ).split("-- Indexes for dumped tables")[0] # remove primary key clauses
    
    if write_to_file != "":    
        with open(write_to_file, mode="w", encoding="utf-8") as output:
            output.write(text)

    return text

def seed_db(script: str, connection_string=":memory:") -> sqlite3.Connection:
    """Will connect to a sqlite database and seed it with the provided script

    :param script: contains the script to be executet on the database
    :connection_string: path to the sqlite .db-file. Defaults to in-memory database
    :return: the sqlite3.Connection object for the database
    """
    con = sqlite3.connect(connection_string)
    cur = con.cursor()
    cur.executescript(script)
    return con


if __name__ == "__main__":
    file = input("Welche sql-dump Datei soll bereinigt werden: ")
    name = input("Bitte den Nachnamen eines Mitglieds angeben: ")
    script = clean_dump(file)
    cur = seed_db(script).cursor()
    cur.execute(f"SELECT * FROM table_mitglieder WHERE nachname='{name}'")
    res = cur.fetchall()
    pprint(res)

