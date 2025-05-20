import customtkinter as ctk
import requests
import os
import json
from dotenv import load_dotenv

# ========== CONFIGURAÇÕES ==========
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ========== VARIÁVEIS ==========
conversa_atual = []
nome_conversa_atual = None
caminho_conversas = "conversas"
conversas_disponiveis = {}

os.makedirs(caminho_conversas, exist_ok=True)

# ========== FUNÇÕES GEMINI ==========
def perguntar_ao_gemini(pergunta):
    conversa_atual.append({"role": "user", "text": pergunta})

    contents = [{"parts": [{"text": msg["text"]}]} for msg in conversa_atual]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = { "Content-Type": "application/json" }

    response = requests.post(url, headers=headers, json={"contents": contents})
    
    if response.status_code == 200:
        resposta = response.json()['candidates'][0]['content']['parts'][0]['text']
        conversa_atual.append({"role": "model", "text": resposta})
        return resposta
    else:
        return f"Erro: {response.status_code} - {response.text}"

# ========== SALVAR/CARREGAR ==========
def salvar_conversa(nome, conversa):
    caminho = os.path.join(caminho_conversas, f"{nome}.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(conversa, f, ensure_ascii=False, indent=2)

def carregar_conversas_salvas():
    historico_lista.configure(state="normal")
    historico_lista.delete("1.0", ctk.END)
    conversas_disponiveis.clear()

    for arquivo in os.listdir(caminho_conversas):
        if arquivo.endswith(".json"):
            nome = arquivo.replace(".json", "")
            conversas_disponiveis[nome] = os.path.join(caminho_conversas, arquivo)
            historico_lista.insert("end", nome + "\n")

    historico_lista.configure(state="disabled")

def selecionar_conversa(event):
    global conversa_atual, nome_conversa_atual

    try:
        selecionado = historico_lista.get("sel.first", "sel.last").strip()
        if selecionado in conversas_disponiveis:
            with open(conversas_disponiveis[selecionado], "r", encoding="utf-8") as f:
                conversa_atual = json.load(f)
            nome_conversa_atual = selecionado

            chatbox.configure(state="normal")
            chatbox.delete("1.0", ctk.END)
            for msg in conversa_atual:
                prefixo = "👤 Você" if msg["role"] == "user" else "🤖 Gemini"
                chatbox.insert("end", f"{prefixo}: {msg['text']}\n\n")
            chatbox.configure(state="disabled")
    except:
        pass

# ========== FUNÇÕES DE UI ==========
def adicionar_ao_chat(mensagem):
    chatbox.configure(state="normal")
    chatbox.insert("end", mensagem + "\n\n")
    chatbox.configure(state="disabled")
    chatbox.see("end")

def enviar(event=None):
    global nome_conversa_atual

    pergunta = entrada.get().strip()
    if not pergunta:
        return
    entrada.delete(0, ctk.END)

    adicionar_ao_chat(f"👤 Você: {pergunta}")
    resposta = perguntar_ao_gemini(pergunta)
    adicionar_ao_chat(f"Resposta IA: {resposta}")

    if nome_conversa_atual:
        salvar_conversa(nome_conversa_atual, conversa_atual)
        carregar_conversas_salvas()

def novo_chat():
    global conversa_atual, nome_conversa_atual
    nome_conversa_atual = f"Chat {len(conversas_disponiveis) + 1}"
    conversa_atual = []

    chatbox.configure(state="normal")
    chatbox.delete("1.0", ctk.END)
    chatbox.configure(state="disabled")

def limpar_historico():
    for arquivo in os.listdir(caminho_conversas):
        if arquivo.endswith(".json"):
            os.remove(os.path.join(caminho_conversas, arquivo))
    carregar_conversas_salvas()

# ========== INTERFACE ==========
app = ctk.CTk()
app.geometry("800x600")
app.title("Chatbot do Marco ✨")

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Histórico lateral
sidebar = ctk.CTkFrame(main_frame, width=180)
sidebar.pack(side="left", fill="y", padx=(0, 10))

historico_label = ctk.CTkLabel(sidebar, text="Histórico")
historico_label.pack(pady=(10, 5))

historico_lista = ctk.CTkTextbox(sidebar, height=500, width=160)
historico_lista.pack(pady=5, padx=5)
historico_lista.configure(state="disabled")
historico_lista.bind("<ButtonRelease-1>", selecionar_conversa)

botao_novo_chat = ctk.CTkButton(sidebar, text="🆕 Novo Chat", command=novo_chat)
botao_novo_chat.pack(pady=5)

botao_limpar_hist = ctk.CTkButton(sidebar, text="🗑️ Limpar Histórico", command=limpar_historico)
botao_limpar_hist.pack(pady=(0, 10))

# Chat principal
chat_frame = ctk.CTkFrame(main_frame)
chat_frame.pack(side="right", fill="both", expand=True)

chatbox = ctk.CTkTextbox(chat_frame, wrap="word", state="disabled")
chatbox.pack(fill="both", expand=True, padx=10, pady=(10, 5))

# Entrada e botão
input_frame = ctk.CTkFrame(app)
input_frame.pack(fill="x", padx=10, pady=(0, 10))

entrada = ctk.CTkEntry(input_frame, placeholder_text="Digite sua pergunta...", width=600)
entrada.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)
entrada.bind("<Return>", enviar)

botao_enviar = ctk.CTkButton(input_frame, text="Enviar", command=enviar)
botao_enviar.pack(side="right", padx=(0, 10), pady=5)

# Inicializa histórico
carregar_conversas_salvas()
app.mainloop()
# ========== FIM ==========