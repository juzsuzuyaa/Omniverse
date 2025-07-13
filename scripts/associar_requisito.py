import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2]
requerimento = sys.argv[3]

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True
)
cursor = conexao.cursor(dictionary=True)

try:
    # Verificar se é admin
    cursor.execute("SELECT administrador FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    admin = cursor.fetchone()

    if not admin or not admin['administrador']:
        print("❌ Você não tem permissão para associar requerimentos.")
        sys.exit()

    # Buscar jogador pelo nickname
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    # Buscar requerimento pelo nome
    cursor.execute("SELECT id FROM requerimentos_tecnicas WHERE nome = %s", (requerimento,))
    req = cursor.fetchone()

    if not req:
        print("❌ Requerimento não encontrado.")
        sys.exit()

    # Verificar se já está associado
    cursor.execute("""
        SELECT 1 FROM jogadores_requisitos 
        WHERE jogadores_id = %s AND requisito_id = %s
    """, (jogador['numero_registro'], req['id']))
    ja_possui = cursor.fetchone()

    if ja_possui:
        print(f"⚠️ {nickname} já possui o requerimento: {requerimento}. Nenhuma ação foi realizada.")
        sys.exit()

    # Inserir associação
    cursor.execute("""
        INSERT INTO jogadores_requisitos (jogadores_id, requisito_id) 
        VALUES (%s, %s)
    """, (jogador['numero_registro'], req['id']))
    conexao.commit()

    print(f"✅ Requerimento associado com sucesso!\n")
    print(f"📌 {nickname} agora possui o requerimento: {requerimento} ✅")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    cursor.close()
    conexao.close()
