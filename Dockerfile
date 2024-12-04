# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos e instala as dependências
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copia o código da aplicação para o diretório de trabalho
COPY . .

# Exponha a porta que o aplicativo vai rodar
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["sh", "start.sh"]
