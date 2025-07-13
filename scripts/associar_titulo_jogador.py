import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if len(sys.argv) < 3:
    print("❌ Uso incorreto. Envie o nome do jogador seguido do título.")
    sys.exit()

nickname = sys.argv[2]
titulo_nome = ' '.join(sys.argv[3:])
numero = sys.argv[1]

try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="omniverse",
        ssl_disabled=True
    )
    cursor = conexao.cursor(dictionary=True)
    # Verificar se o jogador é administrador
    cursor.execute("SELECT administrador FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    if not jogador['administrador']:
        print("❌ Você não tem permissão para adicionar títulos.")
        sys.exit()

    # Verifica se jogador existe
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    jogador_id = jogador['numero_registro']

    # Verifica se o título já existe
    cursor.execute("SELECT id FROM titulos WHERE nome = %s", (titulo_nome,))
    titulo = cursor.fetchone()

    if not titulo:
        # Cria o título
        cursor.execute("INSERT INTO titulos (nome) VALUES (%s)", (titulo_nome,))
        conexao.commit()
        titulo_id = cursor.lastrowid
    else:
        titulo_id = titulo['id']

    # Verifica se o jogador já possui esse título
    cursor.execute("""
        SELECT 1 FROM jogador_titulos 
        WHERE jogador_registro = %s AND titulo_id = %s
    """, (jogador_id, titulo_id))
    ja_possui = cursor.fetchone()

    if ja_possui:
        print(f"⚠️ {nickname} já possui o título: {titulo_nome}")
    else:
        # Associa o título ao jogador
        cursor.execute("""
            INSERT INTO jogador_titulos (jogador_registro, titulo_id) 
            VALUES (%s, %s)
        """, (jogador_id, titulo_id))
        conexao.commit()
        print(f"✅ Título '{titulo_nome}' foi atribuído ao jogador {nickname} com sucesso!")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    if cursor: cursor.close()
    if conexao and conexao.is_connected(): conexao.close()
