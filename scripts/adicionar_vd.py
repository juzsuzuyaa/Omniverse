import sys
import mysql.connector
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2]
vd = sys.argv[3].upper() # Garante que V ou D esteja em maiúsculo
quantidade = int(sys.argv[4])

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
        print("❌ Você não tem permissão para adicionar vitórias/derrotas.")
        sys.exit()

    # Buscar o jogador pelo nickname
    cursor.execute("SELECT numero_registro, v_d FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    # Extrair vitórias e derrotas atuais
    v_d_atual = jogador['v_d']
    vitorias_atual, derrotas_atual = map(int, re.findall(r'\d+', v_d_atual))

    if vd == "V":
        novas_vitorias = vitorias_atual + quantidade
        novas_derrotas = derrotas_atual
        mensagem = f"✅ {quantidade} vitórias adicionadas para {nickname}!"
    elif vd == "D":
        novas_vitorias = vitorias_atual
        novas_derrotas = derrotas_atual + quantidade
        mensagem = f"✅ {quantidade} derrotas adicionadas para {nickname}!"

    # Formatar o novo valor de v_d
    novo_v_d = f"V: {novas_vitorias}/D: {novas_derrotas}"

    cursor.execute("UPDATE jogadores SET v_d = %s WHERE numero_registro = %s", (novo_v_d, jogador['numero_registro']))
    #cursor.execute("INSERT INTO logs (id_jogador, acao, detalhes) VALUES (%s, 'vd', %s)", (jogador['numero_registro'], f"Adicionou {quantidade} {vd} para {nickname}."))
    conexao.commit()

    print(mensagem)

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()