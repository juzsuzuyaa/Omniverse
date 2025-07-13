import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2]
nome_aeternal = sys.argv[3]

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
        print("❌ Você não tem permissão para adicionar Aeternals.")
        sys.exit()

    # Buscar jogador pelo nickname
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    # Buscar Aeternal pelo nome
    cursor.execute("SELECT id, vida FROM aeternals WHERE nome = %s", (nome_aeternal,))
    aeternal = cursor.fetchone()

    if not aeternal:
        print("❌ Aeternal não encontrado.")
        sys.exit()

    # Verificar se já está associado
    cursor.execute("""
        SELECT 1 FROM jogador_aeternals
        WHERE id_jogador = %s AND id_aeternal = %s
    """, (jogador['numero_registro'], aeternal['id']))
    ja_possui = cursor.fetchone()

    if ja_possui:
        print(f"⚠️ {nickname} já possui o Aeternal: {nome_aeternal}. Nenhuma ação foi realizada.")
        sys.exit()

    # Inserir na tabela jogador_aeternals com vida inicial do Aeternal
    cursor.execute("""
        INSERT INTO jogador_aeternals (id_jogador, id_aeternal, vida)
        VALUES (%s, %s, %s)
    """, (jogador['numero_registro'], aeternal['id'], aeternal['vida']))
    conexao.commit()

    print(f"✅ Aeternal adicionado com sucesso!\n")
    print(f"🧬 {nickname} agora possui o Aeternal: {nome_aeternal} ✅")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    cursor.close()
    conexao.close()
