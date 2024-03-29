import sqlite3

from .util import ftext, fdate, get_year

class Database:

    def __init__(self, connection_string=":memory:"):
        self.con = sqlite3.connect(connection_string)
        self.cur = self.con.cursor()

        self.query_member = "SELECT * FROM table_mitglieder WHERE id={mid};"
        self.query_group = "SELECT * FROM table_gruppenzugehoerigkeit WHERE mid={mid};"
        self.query_lby = "SELECT datum FROM table_rechnungen WHERE mid={mid} AND beschreibung=\"Jahresbeitrag\" ORDER BY datum DESC LIMIT 1"
    
    def seed(self, script: str):
        self.cur.executescript(script)

    def lookup_member(self, id: int) -> dict:
        """Get member query from database with given id

        :param con: database connection
        :param id: id for the where clause
        :return: returns result set of query
        """
        res_member = self.cur.execute(self.query_member.format(mid=id)).fetchall()
        res_group = self.cur.execute(self.query_group.format(mid=id)).fetchall()
    
        res_group = {g[1] for g in res_group}

        res_lby = self.cur.execute(self.query_lby.format(mid=id)).fetchall()
        res_lby = get_year(res_lby[0][0]) if len(res_lby) == 1 else None

        if res_member == []:
            return set()
        else:
            res_member = res_member[0]
            return {
                "id": res_member[0],
                "surname": ftext(res_member[2]),
                "notes": res_member[8],
                "groups": res_group,
                "lby": res_lby
            }
        
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
    
insert_fee = lambda mid, date, amount: f"INSERT INTO TABLE table_rechnungen(mid, datum, beschreibung, betrag, buchung) VALUES({mid}, {fdate(date)}, \'Jahresbeitrag\', {amount}, {amount});\n"
insert_don = lambda mid, date, donation: f"INSERT INTO TABLE table_rechnungen(mid, datum, beschreibung, betrag, buchung) VALUES({mid}, {fdate(date)}, \'Spende\', {donation}, {donation});\n"
