import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
nickname = ' '.join(sys.argv[1:])

try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="omniverse",
        ssl_disabled=True
    )
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    jogador_id = jogador['numero_registro']

    cursor.execute("""
        SELECT t.nome FROM jogador_titulos tj
        JOIN titulos t ON tj.titulo_id = t.id
        WHERE tj.jogador_registro = %s
    """, (jogador_id,))
    titulos = cursor.fetchall()

    if not titulos:
        print(f"ℹ️ O jogador *{nickname.upper()}* ainda não possui títulos.")
        sys.exit()
    else:
        mensagem = (
            "*🍃| 🏆 TÍTULOS E TROFÉUS 🏆 | 🍃*\n\n"
            "Este espaço é reservado para registrar as conquistas oficiais dos jogadores dentro do *RPG The Omniverse.* "
            "Aqui serão listados títulos obtidos em eventos, torneios e classificações especiais, representando sua glória, "
            "desempenho e trajetória no jogo.\n\n"
            f"*🍃|📋 TÍTULOS DE {nickname.upper()}:*\n\n"
        )
    for titulo in titulos:
        mensagem += f"* {titulo['nome']}\n"
    print(mensagem)


except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro inesperado: {erro}")
finally:
    if cursor: cursor.close()
    if conexao and conexao.is_connected(): conexao.close()
