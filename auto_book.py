import sqlite3
from pprint import pprint
import pandas as pd

##################### DB STUFF ################################################

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

############### DATA STUFF #################################################

def get_distinct_titles(con: sqlite3.Connection) -> list:
    res = con.cursor().execute("SELECT DISTINCT(titel) FROM table_mitglieder")
    # filter empty titel-fields
    return [item for t in res for item in t if item not in ("", " ", None)]

def parse_fullinfo(text: str) -> pd.Series:
    """Parse the single column text into ["sender", "text", "reference", "iban", "bic"].
    
    :param text: contains all the neccessary information as one string
    :return: returns the information as separate columns
    """
    if text.find("Auftraggeber: ") == 0:
        text = text[14:]    # drop the leading `Auftraggeber: `

    ref = info = bic = iban = None
    if " BIC Auftraggeber: " in text:
        text, bic = text.split(" BIC Auftraggeber: ")
    if " IBAN Auftraggeber: " in text:
        text, iban = text.split(" IBAN Auftraggeber: ")
    if " Zahlungsreferenz: " in text:
        text, ref = text.split(" Zahlungsreferenz: ")
    if " Verwendungszweck: " in text:
        text, info = text.split(" Verwendungszweck: ")

    return pd.Series([text, info, ref, iban, bic], ["sender", "text", "reference", "iban", "bic"])

def read_and_parse_csv(file: str) -> pd.core.frame.DataFrame:
    df_eh = pd.read_csv(
        file, delimiter=";", decimal=",", header=None,
        usecols=[0, 1, 3, 4],
        names=["date", "fullinfo", "amount", "currency"]
    )

    # drop `outgoing` rows
    df_eh = df_eh.loc[df_eh.amount > 0]

    # parse the information into separate columns
    parsed_info = df_eh.fullinfo.apply(lambda x: parse_fullinfo(x))
    df_eh = pd.concat([df_eh, parsed_info], axis=1)
    df_eh = df_eh.drop(columns=["fullinfo"])

    # set column order
    df_eh = df_eh[["date", "sender", "amount", "currency", "reference", "text", "iban", "bic"]]

    return df_eh

if __name__ == "__main__":
    file = input("Welche sql-dump Datei soll bereinigt werden: ")
    script = clean_dump(file)
    con = seed_db(script)
    titel = get_distinct_titles(con)
    df_eh = read_and_parse_csv("daten.csv")
    

