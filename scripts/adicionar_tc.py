import sys
import mysql.connector
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2]
quantidade = int(sys.argv[3])

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
cursor = conexao.cursor(dictionary=True)

try:
    # Verificar se o jogador que está executando o comando é um administrador
    cursor.execute("SELECT administrador FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador_admin = cursor.fetchone()

    if not jogador_admin or not jogador_admin['administrador']:
        print("❌ Você não tem permissão para adicionar TC.")
        sys.exit()

    # Buscar o jogador pelo nickname
    cursor.execute("SELECT numero_registro, moedas_treino FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    # Extrair moedas de treino atuais
    moedas_treino_atual = int(jogador['moedas_treino'])
    novas_moedas_treino = moedas_treino_atual + quantidade
    mensagem = f"✅ {quantidade} moedas de treino adicionadas para {nickname}!"

    cursor.execute("UPDATE jogadores SET moedas_treino = %s WHERE numero_registro = %s", (novas_moedas_treino, jogador['numero_registro']))
    cursor.execute("INSERT INTO logs (id_jogador, acao, detalhes) VALUES (%s, 'adicao', %s)", (jogador['numero_registro'], f"Adicionados {quantidade} TC para {nickname}."))
    conexao.commit()

    print(mensagem)

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()