import pandas as pd

class Data:

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
    
    def read_and_parse_csv(file: str) -> pd.DataFrame:
        """Reads data-csv into pandas dataframe and restructures data as needed
        
        :param file: path to .csv file
        :return: the pandas dataframe containing the data
        """
        df_eh = pd.read_csv(
            file, delimiter=";", decimal=",", header=None,
            usecols=[0, 1, 3, 4],
            names=["date", "fullinfo", "amount", "currency"]
        )
    
        # drop `outgoing` rows
        df_eh = df_eh.loc[df_eh.amount > 0]
    
        # parse the information into separate columns
        parsed_info = df_eh.fullinfo.apply(lambda x: Data.parse_fullinfo(x))
        df_eh = pd.concat([df_eh, parsed_info], axis=1)
        df_eh = df_eh.drop(columns=["fullinfo"])
    
        # set column order
        df_eh = df_eh[["date", "sender", "amount", "currency", "reference", "text", "iban", "bic"]]
    
        return df_eh