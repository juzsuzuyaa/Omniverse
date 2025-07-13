import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

nome_completo = sys.argv[1]  # Ex: "Last Lenus"

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True
)
cursor = conexao.cursor(dictionary=True)

try:
    # Buscar jogador pelo nickname
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nome_completo,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    jogador_id = jogador['numero_registro']

    # Obter os requisitos que o jogador possui
    cursor.execute("""
        SELECT rt.nome
        FROM jogadores_requisitos jr
        JOIN requerimentos_tecnicas rt ON jr.requisito_id = rt.id
        WHERE jr.jogadores_id = %s
    """, (jogador_id,))
    requisitos = cursor.fetchall()

    if not requisitos:
        print(f"📋 *{nome_completo}* ainda não possui nenhum requisito associado.")
        sys.exit()

    mensagem = f"📋 *Requisitos de {nome_completo}:*\n\n"
    for r in requisitos:
        mensagem += f"✅ {r['nome']}\n"

    print(mensagem)

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()
