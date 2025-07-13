import io
import sys
import mysql.connector

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    if len(sys.argv) < 2:
        print("Uso: python3 log.py [numero_whatsapp]", file=sys.stderr)
        sys.exit(1)

    numero_whatsapp = sys.argv[1]

    conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
    cursor = conexao.cursor(dictionary=True)

    # Obter o ID do jogador
    cursor.execute("SELECT numero_registro, administrador FROM jogadores WHERE numero_whatsapp = %s", (numero_whatsapp,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado.", file=sys.stderr)
        sys.exit(1)

    jogador_id = jogador["numero_registro"]
    administrador = jogador["administrador"]

    # Verificar se o jogador é administrador
    if not administrador:
        print("Você não tem permissão para visualizar o log.", file=sys.stderr)
        sys.exit(1)

    # Consultar o log e os nicknames dos jogadores
    cursor.execute("""
        SELECT j.nickname, l.acao, l.detalhes
        FROM logs l
        JOIN jogadores j ON l.id_jogador = j.numero_registro
        ORDER BY l.id_jogador, CASE l.acao
            WHEN 'compra' THEN 1
            WHEN 'upgrade' THEN 2
            WHEN 'upgrade_tecnica' THEN 3
            WHEN 'aeternal' THEN 4
            ELSE 5
        END
    """)

    log = cursor.fetchall()

    # Exibir o log formatado
    print("*💠Log de movimentação💠*\n")
    for logs in log:
        print(f"\n🔰{logs['nickname']}, {logs['detalhes']}")

except mysql.connector.Error as err:
    print(f"Erro de banco de dados: {err}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Erro inesperado: {e}", file=sys.stderr)
    sys.exit(1)

finally:
    if cursor:
        cursor.close()
    if conexao and conexao.is_connected():
        conexao.close()