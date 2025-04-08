class FakeAnalyzer:
    def __init__(self):
        self.name = None
        self.busy = False
        self.supported_codes = {"Ledetect": [619, 311], "Biorad": [548, 258]}

    def send_order(self, name, patient_id, services):
        if not name:
            raise Exception(f"Analyzer with name '{name}' not found")

        if self.busy:
            raise Exception("Analyzer is busy")

        if not all(s["serviceCode"] in self.supported_codes.get(name, []) for s in services):
            raise Exception("Analyzer can not do this order.")

        self.busy = True
        return {"status": "accepted"}

    def get_status(self):
        if not self.busy:
            raise Exception("Analyzer is not working.")

        self.busy = False
        return {"patient": "123", "services": [{"code": 619, "result": "77"}]}
