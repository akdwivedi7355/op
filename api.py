from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server = "localhost"
database = "tt"

# Pydantic model for request validation
class UserRequest(BaseModel):
    type_: int
    id_: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    class_: Optional[str] = None
    college: Optional[str] = None
    country: Optional[str] = None
    dob: Optional[str] = None
    mobile_no: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None

def execute_stored_procedure(request: UserRequest):
    try:
        print("🔹 Connecting to Database...")
        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
        cursor = conn.cursor()

        print(f"🔹 Executing Stored Procedure with params: {request.dict()}")

        cursor.execute(
            "{CALL SP_UserDetails(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}",
            request.type_, request.id_, request.address, request.city, 
            request.class_, request.college, request.country, request.dob, 
            request.mobile_no, request.name, request.state
        )

        # Fetch all results and convert to dictionary
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        print(f"✅ Query Result: {result}")

        conn.commit()
        conn.close()

        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/")
def user_operation(request: UserRequest):
    """
    Handle User Operations:
    Type 1 = Insert, Type 2 = Update, Type 3 = Delete, Type 4 = Select
    """
    print("🔹 Received API Request")
    
    try:
        data = execute_stored_procedure(request)
        print(f"✅ Success Response: {data}")
        return {"success": True, "data": data}
    
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
