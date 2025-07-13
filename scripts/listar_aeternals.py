import io
import sys
import mysql.connector

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    if len(sys.argv) < 2:
        print("Uso: python3 listar_aeternals.py [numero_whatsapp]", file=sys.stderr)
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
    cursor.execute("SELECT numero_registro FROM jogadores WHERE numero_whatsapp = %s", (numero_whatsapp,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado.", file=sys.stderr)
        sys.exit(1)

    jogador_id = jogador["numero_registro"]

    # Obtém os aeternals do jogador com a vida e o nível
    cursor.execute("""
        SELECT a.nome, ja.vida AS jogador_vida, a.vida AS aeternal_vida
        FROM aeternals a
        JOIN jogador_aeternals ja ON a.id = ja.id_aeternal
        WHERE ja.id_jogador = %s
    """, (jogador_id,))
    aeternals = cursor.fetchall()

    if aeternals:
        mensagem = "✅ *Lista de Aeternals!*\n\n"
        mensagem += "🔹 *Aqui estão os Aeternals que você possui:*\n\n"
        for aeternal in aeternals:
            nivel = aeternal['jogador_vida'] // aeternal['aeternal_vida']
            mensagem += f"🥚 *{aeternal['nome']}*\n"
            mensagem += f"\t• ❤️ *Vida:* {aeternal['jogador_vida']:,}\n"
            mensagem += f"\t• ⭐ *Nível:* {nivel}\n\n"
        mensagem += "💡 *Treine e fortaleça seus Aeternals para desbloquear todo o seu potencial!* 🚀🔥"
        print(mensagem)
    else:
        print("❌ *Nenhum Aeternal Encontrado!*\n\n"
              "⚠️ Você *não possui nenhum Aeternal no momento.*\n\n"
              "🔍 *Dica:*\n"
              "\t• _Para obter um Aeternal, participe de eventos, explore o mercado ou adquira através de métodos disponíveis no jogo!_\n\n"
              "🚀 *Continue sua jornada e conquiste seu primeiro Aeternal!* 💪🔥")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}", file=sys.stderr)
    sys.exit(1)
except Exception as erro:
    print(f"Erro: {erro}", file=sys.stderr)
    sys.exit(1)

finally:
    if cursor:
        cursor.close()
    if conexao and conexao.is_connected():
        conexao.close()
