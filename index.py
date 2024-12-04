from flask import Flask, request, jsonify
from flask_cors import CORS  # Importar o CORS
import re
import mysql.connector  # Para conectar ao MySQL
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Baixar dados necessários para o NLTK (somente na primeira vez)
nltk.download('punkt')

# Configuração do banco de dados usando variáveis de ambiente
db_config = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}

# Função para conectar ao banco de dados e obter perguntas e respostas
def get_perguntas_respostas():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT pergunta, resposta FROM perguntas_respostas")
    resultados = cursor.fetchall()
    
    perguntas = [resultado['pergunta'] for resultado in resultados]
    respostas = [resultado['resposta'] for resultado in resultados]
    
    cursor.close()
    connection.close()
    
    return perguntas, respostas

# Buscar perguntas e respostas diretamente do banco de dados
perguntas, respostas = get_perguntas_respostas()

# Função para pré-processar texto
def preprocess(text):
    text = text.lower()  # Coloca tudo em letras minúsculas
    text = re.sub(r'\W+', ' ', text)  # Remove caracteres especiais
    return text

# Pré-processar todas as perguntas
perguntas_preprocessadas = [preprocess(pergunta) for pergunta in perguntas]

# Criar modelo TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(perguntas_preprocessadas)

# Função para encontrar a melhor resposta
def buscar_resposta(pergunta_usuario):
    pergunta_usuario = preprocess(pergunta_usuario)  # Pré-processar a pergunta do usuário
    usuario_tfidf = vectorizer.transform([pergunta_usuario])  # Converter para TF-IDF
    similaridades = cosine_similarity(usuario_tfidf, tfidf_matrix)  # Comparar com as perguntas
    
    # Verificar a similaridade máxima
    similaridade_maxima = similaridades.max()

    # Se a similaridade for abaixo de um limite (por exemplo, 0.2), retorna uma mensagem de não entendimento
    if (similaridade_maxima < 0.2):  # Limite de similaridade ajustável
        return "Desculpe, não entendi a sua pergunta. Pode reformular?"

    # Caso contrário, retorna a resposta correspondente à pergunta mais similar
    indice_max = similaridades.argmax()  # Encontra a pergunta mais similar
    return respostas[indice_max]

# Criar API Flask
app = Flask(__name__)
CORS(app)  # Permitir todas as origens para todas as rotas

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    pergunta_usuario = data.get('pergunta')
    resposta = buscar_resposta(pergunta_usuario)
    return jsonify({'resposta': resposta})

if __name__ == '__main__':
    # Rodar o Flask na porta 5000 e tornar o servidor acessível de fora do contêiner
    app.run(debug=True, host='0.0.0.0', port=5000)
