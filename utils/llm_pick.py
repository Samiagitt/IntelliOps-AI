from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

def pick_llm(Level:str):
    """
    Picks the appropriate LLM based on the level of the question.
    Args:
    level(str): The level of the question, can be "low", "medium","high".
    Returns: str: The name of the LLM to be used
    """
    
    if Level.lower() == "low":
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    elif Level.lower() =="medium":
        llm= ChatOpenAI(model_name="gpt-5.6-terra", temperature=0)
    elif Level=="high":
        llm= ChatOpenAI(model_name="gpt-5.6-sol", temperature=0)
    else:
        raise ValueError(f"Unsupported level: {Level}")
    
    return llm

llm_obj=pick_llm("low")
print(llm_obj.invoke("whats the cpital of france?").content)