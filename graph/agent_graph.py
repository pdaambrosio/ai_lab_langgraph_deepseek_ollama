import re
import json
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from tools.custom_tools import TOOLS

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOllama(model="deepseek-r1:1.5b", temperature=0.1)

SYSTEM_PROMPT = """Você é um assistente inteligente em português. Você pode pensar livremente, mas sua resposta final deve seguir este formato exato:

Se você precisar usar uma ferramenta para responder ao usuário, termine sua resposta fornecendo APENAS este JSON estruturado:
{"acao": "NOME_DA_FERRAMENTA", "parametros": {"NOME_DO_PARAMETRO": VALOR}}

Ferramentas disponíveis:
- somar_numeros (parâmetros obrigatórios: "a" [inteiro], "b" [inteiro])
- obter_horario_atual (não aceita parâmetros)

Se você NÃO precisar de ferramentas para responder (como em saudações ou conversas simples), responda textualmente de forma direta e natural ao usuário.
"""

def extract_final_text(message_content: str) -> str:
    return re.sub(r"<think>.*?</think>", "", message_content, flags=re.DOTALL).strip()

def validate_and_extract_json(text: str) -> tuple[bool, dict | None, str | None]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return False, None, "Nenhum bloco JSON foi encontrado na sua resposta."
    try:
        data = json.loads(match.group(0))
        if "acao" not in data:
            return False, None, "O JSON enviado não contém a chave obrigatória 'acao'."
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"O formato do seu JSON está inválido. Erro de sintaxe: {str(e)}"

def call_model(state: AgentState):
    message = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in message):
        message = [SystemMessage(content=SYSTEM_PROMPT)] + message
    response = llm.invoke(message)
    return {"messages": [response]}

def execute_tool(state: AgentState):
    last_message = state["messages"][-1].content
    clean_text = extract_final_text(last_message)
    success, data_tool, error_msg = validate_and_extract_json(clean_text)
    
    if not success:
        response_content = f"Erro do Sistema: Comando inválido. Detalhes: {error_msg}"
        return {"messages": [HumanMessage(content=response_content)]}
    
    action_name = data_tool.get("acao")
    params = data_tool.get("parametros", {})
    
    if action_name in TOOLS:
        funcao = TOOLS[action_name]
        try:
            resultado = funcao(**params) if params else funcao()
            response_content = f"Resultado retornado pela ferramenta {action_name}: {resultado}"
        except Exception as e:
            response_content = f"Erro ao executar a função interna '{action_name}': {str(e)}"
    else:
        response_content = f"Erro do Sistema: A ferramenta '{action_name}' não existe no sistema."
        
    return {"messages": [HumanMessage(content=response_content)]}

def route_next_step(state: AgentState) -> Literal["ferramenta", END]:
    last_message = state["messages"][-1].content
    clean_text = extract_final_text(last_message)
    if '"acao"' in clean_text or "acao" in clean_text or clean_text.startswith("{"):
        return "ferramenta"
    return END

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("agente", call_model)
    workflow.add_node("ferramenta", execute_tool)
    workflow.add_edge(START, "agente")
    workflow.add_conditional_edges("agente", route_next_step)
    workflow.add_edge("ferramenta", "agente")
    return workflow.compile()
