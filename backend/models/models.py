from pydantic import BaseModel

class LaboratoryService(BaseModel):
    patient_id: str
    service_code: int
    status: str = 'pending'
    result: str = None
    deviation: float = None
    analyzer_name: str = None