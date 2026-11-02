import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from utils.llm_pick import pick_llm
from Models.schema import AgentSchema

#---------------------------------AI Agent Code---------------------------------------------

#Curate_qsn LLM node
def curate_question(state: AgentSchema)->AgentSchema:
    user_question= state['user_question']
    llm=pick_llm("low")
    response=llm.invoke(f"curate the following question: {user_question}")
    
    return state

#Add_context node
def prompt_query(state: AgentSchema)->AgentSchema:
    curated_question=state["curated_question"]
    
    
    
    