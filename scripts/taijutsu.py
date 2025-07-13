import io
import sys
import mysql.connector
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    if len(sys.argv) < 3:
        print("Uso: python3 taijutsu.py [numero_whatsapp] [nome_taijutsu]", file=sys.stderr)
        sys.exit(1)

    numero_whatsapp = sys.argv[1]
    nome_taijutsu = sys.argv[2]

    conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT numero_registro, forca FROM jogadores WHERE numero_whatsapp = %s", (numero_whatsapp,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado.", file=sys.stderr)
        sys.exit(1)

    jogador_registro = jogador["numero_registro"]
    forca = (jogador["forca"])

    cursor.execute("""
    SELECT jt.nivel_upgrade, t.id AS tecnica_id, t.nome, t.card, t.fisico
    FROM jogador_tecnicas jt
    JOIN tecnicas t ON jt.tecnica_id = t.id
    WHERE jt.jogador_registro = %s 
    AND LOWER(t.nome) = %s
    AND (t.fisico = 1)
""", (jogador_registro, nome_taijutsu.lower()))

    taijutsu = cursor.fetchone()

    if not taijutsu:
        print("❌ Você não possui esse Taijutsu! Verifique o nome e tente novamente.")
        sys.exit()

    # Calcular Attack Power
    attack_power = forca * 5
    attack_power_formatado = f"{attack_power:,}".replace(".", ",")

    # Atualizar o card com o novo Attack Power
    card_atualizado = re.sub(r'Attack☆Power:\(🔴[\d,]+%', f'Attack☆Power:(🔴{attack_power_formatado}%', taijutsu["card"])

    # Exibir card atualizado
    sys.stdout.write(card_atualizado)

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
