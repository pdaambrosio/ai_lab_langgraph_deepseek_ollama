from langchain_core.messages import HumanMessage
from graph.agent_graph import build_graph

if __name__ == "__main__":
    app = build_graph()
    user_question = "Por favor, faça a soma de 1250 com 3720. Pode calcular para mim?"
    initial_input = {"messages": [HumanMessage(content=user_question)]}
    
    print("=" * 50)
    print(f"USUÁRIO: {user_question}")
    print("=" * 50)
    print("--- Executando Fluxo do LangGraph ---\n")
    
    for evento in app.stream(initial_input, stream_mode="values"):
        actual_message = evento["messages"][-1]
        author_type = actual_message.__class__.__name__
        print(f"[{author_type}]:")
        print(f"{actual_message.content}")
        print("-" * 40)
