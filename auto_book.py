from Database import *
from Data import *
import re

from pprint import pprint

def uml(txt: str) -> str:
    return txt.lower().replace("ö", "oe").replace("ä", "ae").replace("ü","ue")

def match_with_text(db: Database, sender, text: str) -> int:
    nums = set([int(it) for it in re.findall("\\b\\d{1,5}\\b", text) if int(it) > 0])
    for n in nums:
        person = db.lookup_member(n)
        if person == {}:
            return -1
        if uml(sender).__contains__(uml(person["surname"])):
            return n
    return -1  

def match(db: Database, entry):
    if entry.reference is None:
        if entry.text is None:
            return -1
        return match_with_text(db, entry.sender, entry.text)

    try:
        mid = int(entry.reference)
        return mid
    except (ValueError, TypeError):
        return match_with_text(db, entry.sender, entry.reference)

if __name__ == "__main__":
    db = Database()

    file = input("Welche sql-dump Datei soll bereinigt werden: ")
    amount = int(input("Wie hoch war der Jahresbeitrag?: "))

    script = Database.clean_dump(file)
    db.seed(script)

    df_eh = Data.read_and_parse_csv("daten.csv")

    with open("output.sql", "a", encoding="utf-8") as sql:
        with open("log.txt", "a", encoding="utf8") as log:
            try:
                for entry in df_eh.iloc:
                    pprint(entry, stream=log)
                    guess = match(db, entry)
                    if guess == -1:
                        pprint(entry)
                        uin = input("Zu diesem Datensatz wurde keine ID gefunden.\nWelche soll verwendet werden?: ")
                        if uin=="":
                            print("Datensatz wurde vom Benutzer übersprungen. Keine Buchung!", file=log)
                        else:
                            guess = int(uin)
                            print("ID wurde vom Benutzer ermittelt: " + str(guess), file=log)
                    else:
                        print("ID wurde vom Programm ermittelt: " + str(guess), file=log)
                    print("", file=log)

                    day = entry.date[0:2]
                    mon = entry.date[3:5]
                    yea = entry.date[6:]

                    sql.write(f"INSERT INTO table_rechnungen(mid, datum, beschreibung, betrag, buchung) VALUES({guess}, \'{yea}-{mon}-{day}\', \'Jahresbeitrag\', {amount}, {amount});\n")
                    if float(entry.amount)-amount > 0:
                            sql.write(f"INSERT INTO table_rechnungen(mid, datum, beschreibung, betrag, buchung) VALUES({guess}, \'{yea}-{mon}-{day}\', \'Spende\', {float(entry.amount)-amount}, {float(entry.amount)-amount});\n")
    
            except KeyboardInterrupt:
                print("Bye")
