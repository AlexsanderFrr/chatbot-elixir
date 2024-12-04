from flask import Flask, request, jsonify
from flask_cors import CORS  # Importar o CORS
import json
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Baixar dados necessários para o NLTK (somente na primeira vez)
nltk.download('punkt')

# Carregar perguntas e respostas
with open('faqs.json', 'r', encoding='utf-8') as f:
    faqs = json.load(f)

perguntas = [faq['pergunta'] for faq in faqs]
respostas = [faq['resposta'] for faq in faqs]

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
    if similaridade_maxima < 0.2:  # Limite de similaridade ajustável
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
    app.run(debug=True)
