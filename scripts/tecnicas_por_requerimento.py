import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if len(sys.argv) < 3:
    print("❌ Uso incorreto. Envie o nome do jogador e o nome do requisito.")
    sys.exit()

nickname = sys.argv[1]
requisito_nome = ' '.join(sys.argv[2:])

try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="omniverse",
        ssl_disabled=True
    )
    cursor = conexao.cursor(dictionary=True)

    # Buscar jogador
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"❌ Jogador não encontrado: {nickname}")
        sys.exit()

    jogador_id = jogador['numero_registro']

    # Buscar requisito
    cursor.execute("SELECT id FROM requerimentos_tecnicas WHERE nome = %s", (requisito_nome,))
    requisito = cursor.fetchone()

    if not requisito:
        print(f"❌ Requisito informado não encontrado: {requisito_nome}")
        sys.exit()

    requisito_id = requisito['id']

    # Buscar técnicas que o jogador possui para o requisito
    cursor.execute("""
        SELECT t.nome, t.saikoki_usado, t.poder_ataque, t.resistencia, jt.nivel_upgrade
        FROM jogador_tecnicas jt
        JOIN tecnicas t ON jt.tecnica_id = t.id
        WHERE jt.jogador_registro = %s AND t.requerimento_id = %s
    """, (jogador_id, requisito_id))
    tecnicas = cursor.fetchall()

    if not tecnicas:
        print(f"⚠️ {nickname} não possui técnicas com o requisito: {requisito_nome}.")
        sys.exit()

    # Mensagem formatada
    mensagem = f"🔍 *Técnicas de {nickname}* 🔍\n\n"

    for tecnica in tecnicas:
        nivel = tecnica["nivel_upgrade"]
        saikoki = int(tecnica["saikoki_usado"]) * (2 ** nivel) if tecnica["saikoki_usado"] else 0
        poder_ataque = int(tecnica["poder_ataque"]) * (2 ** nivel) if tecnica["poder_ataque"] else 0
        resistencia = int(tecnica["resistencia"]) * (2 ** nivel) if tecnica["resistencia"] else 0

        mensagem += f"🎯 *{tecnica['nome']}*\n"
        mensagem += f"⚡ *Saikōki Usado:* {saikoki:,}\n"
        mensagem += f"💥 *Poder de Ataque:* {poder_ataque:,}\n"
        mensagem += f"🛡️ *Resistência:* {resistencia:,}\n"
        mensagem += f"📈 *Upgrades:* {nivel}\n"
        mensagem += "--------------------------\n"

    print(mensagem.strip())

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    if cursor: cursor.close()
    if conexao and conexao.is_connected(): conexao.close()
