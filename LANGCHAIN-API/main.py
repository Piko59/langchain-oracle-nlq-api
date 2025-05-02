from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import oracledb
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
import logging

app = FastAPI()

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Oracle DB configuration using LangChain's SQLDatabase(EDIT THIS AREA!!!)
db_uri = "oracle+oracledb://C##PARKING:MyPassword123@oracle-xe:1521/XE"
db = SQLDatabase.from_uri(db_uri)

# Langchain LLM setup
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# Create SQL agent with database toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)

class Query(BaseModel):
    question: str

@app.post("/query")
def query_database(query: Query):
    try:
        question = query.question
        logger.info(f"Received question: {question}")
        
        # Use the SQL agent to process the question without specifying table names
        result = agent.run(f"""
            Answer the following question: {question}
            
            Use the database to find the answer.
            Don't assume any specific table names and discover them automatically.
        """)
        
        logger.info(f"Agent result: {result}")
        
        return {"response": result}
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)