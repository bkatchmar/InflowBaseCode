import datetime

class RequestInputHandler():
    def get_entry_for_float(self,floatAmt):
        try:
            return float(floatAmt)
        except Exception as e:
            return 0.0
        
    def get_entry_for_int(self,int_amt):
        try:
            return int(int_amt)
        except Exception as e:
            return 0
        
    def get_entry_for_date(self,date_val):
        try:
            return datetime.datetime.strptime(date_val, "%b %d %Y")
        except Exception as e:
            return datetime.date.today()