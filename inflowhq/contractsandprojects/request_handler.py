class RequestInputHandler():
    def get_entry_for_float(self,floatAmt):
        try:
            return float(floatAmt)
        except Exception as e:
            return 0.0
        
    def get_entry_for_int(self,intAmt):
        try:
            return int(intAmt)
        except Exception as e:
            return 0