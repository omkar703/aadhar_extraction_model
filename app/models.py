from pydantic import BaseModel, Field
from typing import Optional


class AadhaarResponse(BaseModel):
    """
    Pydantic model for Aadhaar card extraction response.
    All fields are optional as not all information may be present or detected.
    """
    AADHAR_NUMBER: Optional[str] = Field(None, description="12-digit Aadhaar number formatted as XXXX XXXX XXXX")
    NAME: Optional[str] = Field(None, description="Name on the Aadhaar card")
    ADDRESS: Optional[str] = Field(None, description="Address on the Aadhaar card")
    DOB: Optional[str] = Field(None, description="Date of Birth")
    GENDER: Optional[str] = Field(None, description="Gender")
    VID: Optional[str] = Field(None, description="Virtual ID")
    FATHER_NAME: Optional[str] = Field(None, description="Father's name (if present)")
    PHONE_NUMBER: Optional[str] = Field(None, description="Phone number (if present)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "AADHAR_NUMBER": "1234 5678 9012",
                "NAME": "John Doe",
                "ADDRESS": "123 Main Street, City, State - 123456",
                "DOB": "01/01/1990",
                "GENDER": "Male",
                "VID": None
            }
        }
