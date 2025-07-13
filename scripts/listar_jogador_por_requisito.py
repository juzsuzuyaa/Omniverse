import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

nome_requisito = ' '.join(sys.argv[1:]).strip()

try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="omniverse",
        ssl_disabled=True
    )
    cursor = conexao.cursor(dictionary=True)

    # Buscar ID do requisito
    cursor.execute("SELECT id FROM requerimentos_tecnicas WHERE nome = %s", (nome_requisito,))
    requisito = cursor.fetchone()

    if not requisito:
        print(f"❌ Requisito \"{nome_requisito}\" não encontrado.")
        sys.exit()

    requisito_id = requisito['id']

    # Buscar jogadores que possuem esse requisito
    cursor.execute("""
        SELECT j.nickname
        FROM jogadores_requisitos jr
        JOIN jogadores j ON j.numero_registro = jr.jogadores_id
        WHERE jr.requisito_id = %s
    """, (requisito_id,))
    jogadores = cursor.fetchall()

    if not jogadores:
        print(f"⚠️ Nenhum jogador possui o requisito: *{nome_requisito}*.")
    else:
        mensagem = f"📋 *Jogadores com o requisito: {nome_requisito}*\n\n"
        for j in jogadores:
            mensagem += f"🔹 {j['nickname']}\n"
        print(mensagem)

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    if cursor: cursor.close()
    if conexao and conexao.is_connected(): conexao.close()
