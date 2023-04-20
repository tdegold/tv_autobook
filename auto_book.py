from Model.Database import Database, insert_fee, insert_don
from Model.Data import Data
from Model.Predictor import Predictor
from Model.util import split_fee

db = Database()

pred = Predictor(db)

file = input("Welche sql-dump Datei soll bereinigt werden: ")

fee = int(input("Wie hoch war der Jahresbeitrag?: "))

script = Database.clean_dump(file)
db.seed(script)
df_eh = Data.read_and_parse_csv("daten.csv")


for p in df_eh.iloc:
    status, id = pred.match_id(p)
    
    if status == 1:
        amount, donation = split_fee(int(p.amount), fee)

        with open("output.sql", "a", encoding="utf-8") as output:
            output.write(insert_fee(id, p.date, amount))
            if donation > 0:
                output.write(insert_don(id, p.date, donation))

        with open("log.txt", "a", encoding="utf-8") as log:
            log.writelines(str(p))
            log.write(f"\nDatensatz wurde automatisch gebucht mit MID {id}. Betrag={amount}. Spende={donation}.\n\n")

    elif status == 2:
        with open("log.txt", "a", encoding="utf-8") as log:
            log.writelines(str(p))
            log.write(f"\nDatensatz wurde übersprungen, da bereits eine Buchung in diesem Jahr vorhanden ist.\n\n")

    else:
        print(p)

        condition = True
        while condition:
            u_in = input("Es konnte keine ID ermittelt werden. Bitte angeben oder \"skip\": ")
            if u_in.__eq__("skip"):
                with open("log.txt", "a", encoding="utf-8") as log:
                        log.writelines(str(p))
                        log.write(f"\nDatensatz wurde vom User übersprungen.\n\n")
                print("Datensatz wurde übersprungen. Keine Buchung.\n")
                condition = False

            try:
                id = int(u_in)

                cand = db.lookup_member(id)
                cand_id = cand["id"]
                cand_su = cand["surname"]
                code = pred.check_candidate(p.sender, cand)

                ##################################
                if code == 1:
                    with open("output.sql", "a", encoding="utf-8") as output:

                        amount, donation = split_fee(int(p.amount), fee)
            
                        output.write(insert_fee(id, p.date, amount))
                        if donation > 0:
                            output.write(insert_don(id, p.date, donation))
                
                    with open("log.txt", "a", encoding="utf-8") as log:
                        log.writelines(str(p))
                        log.write(f"\nDatensatz wurde vom User gebucht mit MID {id}. Betrag={amount}. Spende={donation}.\n\n")
                
                    print(f"Datensatz wurde vom User gebucht mit MID {id}. Betrag={amount}. Spende={donation}.\n")
                    condition = False
                ######################################
                elif code == 2:
                    with open("log.txt", "a", encoding="utf-8") as log:
                        log.writelines(str(p))
                        log.write(f"\nDatensatz wurde übersprungen, da bereits eine Buchung in diesem Jahr vorhanden ist.\n\n")

                    print(f"Datensatz wurde übersprungen, da bereits eine Buchung in diesem Jahr vorhanden ist.\n\n") 
                    condition = False
                ##########################################
                elif code == -2:
                    print(f"Der Name stimmt überein, die Person ist aber in mind. einer ungewollten Gruppe {p.groups.intersection(pred.exclude_groups)}. Datensatz wird übersprungen.\n")

                    with open("log.txt", "a", encoding="utf-8") as log:
                        log.writelines(str(p))
                        log.write(f"\nDatensatz wurde übersprungen, da die Person in mind. einer ungewollten Gruppe ist. ({p.groups.intersection(pred.exclude_groups)})")
                    condition = False
                ###################################################
                else:
                    print(f"Der Name stimmt nicht überein. Gefunden wurde eine Person mit Nachnamen \"{cand_su}\" und MID {cand_id}.\n")
            except ValueError:
                pass
            