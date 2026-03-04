from dotenv import load_dotenv

load_dotenv() 
from typing import Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

class RestaurantOutput(BaseModel): # Renamed to CamelCase (Python convention)
    name: str = Field(description="Restaurant name")
    address: Optional[str] = Field(None, description="Full Address")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine (e.g., Italian, South Indian)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nilagiri Ruchulu",
                "address": "H-no: 6-2-1320/12, Hyderabad Road, VT Colony, Nalgonda, Telangana 508001",
                "cusine_type": "South Indian"
            }
        }

def get_structured_llm(temperature: float = 0.0, max_output_tokens: int = 2048):
    # 1. Initialize with keyword arguments
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=temperature, 
        max_tokens=max_output_tokens
    )
    
    # 2. Bind the structured output schema
    return model.with_structured_output(RestaurantOutput)

chat_llm = get_structured_llm()