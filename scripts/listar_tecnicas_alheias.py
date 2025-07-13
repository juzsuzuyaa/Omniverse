import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2] if len(sys.argv) > 2 else None

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

    #if not jogador_admin or jogador_admin['administrador'] != 1:
        #print("❌ Você não tem permissão para visualizar técnicas de outros jogadores.")
        #sys.exit()

    # Buscar o jogador pelo nickname
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print(f"❌ Jogador não encontrado. {nickname}")
        sys.exit()

    jogador_id = jogador['numero_registro']

    # Buscar as técnicas associadas ao jogador
    cursor.execute("""
        SELECT t.nome, t.saikoki_usado, t.poder_ataque, t.resistencia, jt.nivel_upgrade
        FROM jogador_tecnicas jt
        JOIN tecnicas t ON jt.tecnica_id = t.id
        WHERE jt.jogador_registro = %s
    """, (jogador_id,))
    
    tecnicas = cursor.fetchall()

    if not tecnicas:
        print(f"📜 {nickname} ainda não possui nenhuma técnica registrada.")
        sys.exit()

    # Montar a mensagem formatada
    mensagem = f"🔍 *Técnicas de {nickname}* 🔍\n\n"

    for tecnica in tecnicas:
        nivel = tecnica["nivel_upgrade"]
        saikoki = int(tecnica["saikoki_usado"]) * (2 ** nivel) if tecnica["saikoki_usado"] else 0
        poder_ataque = int(tecnica["poder_ataque"]) * (2 ** nivel) if tecnica["poder_ataque"] else 0
        resistencia = int(tecnica["resistencia"]) * (2 ** nivel) if tecnica["resistencia"] else 0

        mensagem += f"🎯 *{tecnica['nome']}*\n"
        mensagem += f"⚡ *Saikōki Usado:* {int(saikoki):,}\n"
        mensagem += f"💥 *Poder de Ataque:* {int(poder_ataque):,}\n"
        mensagem += f"🛡️ *Resistência:* {int(resistencia):,}\n"
        mensagem += f"📈 *Upgrades:* {nivel}\n"
        mensagem += "--------------------------\n"

    print(mensagem.strip())

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()
