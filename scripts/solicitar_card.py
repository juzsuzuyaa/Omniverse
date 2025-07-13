import io
import sys
import mysql.connector
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    if len(sys.argv) < 3:
        print("Uso: python3 exibir_card.py [numero_whatsapp] [nome_tecnica]", file=sys.stderr)
        sys.exit(1)

    numero_whatsapp = sys.argv[1]
    nome_tecnica = sys.argv[2]

    conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
    )
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT numero_registro FROM jogadores WHERE numero_whatsapp = %s", (numero_whatsapp,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado.", file=sys.stderr)
        sys.exit(1)

    jogador_registro = jogador["numero_registro"]

    cursor.execute("""
        SELECT jt.nivel_upgrade, t.id AS tecnica_id, t.nome, t.saikoki_usado, t.poder_ataque, t.resistencia, t.card, t.fisico
        FROM jogador_tecnicas jt
        JOIN tecnicas t ON jt.tecnica_id = t.id
        WHERE jt.jogador_registro = %s AND LOWER(t.nome) = %s
    """, (jogador_registro, nome_tecnica.lower()))
    tecnica = cursor.fetchone()

    if not tecnica:
        print("Técnica não encontrada para este jogador.", file=sys.stderr)
        sys.exit(1)

    if tecnica["fisico"] == 1:
        print("Para habilidades físicas utilize o comando *Físico* seguido do nome da técnica.", file=sys.stderr)
        sys.exit(1)

    nivel_atual = tecnica["nivel_upgrade"]
    poder_ataque_base = int(tecnica["poder_ataque"].replace(',', '')) if tecnica["poder_ataque"] else 0
    resistencia_base = int(tecnica["resistencia"].replace(',', '')) if tecnica["resistencia"] else 0
    saikoki_base = int(tecnica["saikoki_usado"].replace(',', ''))

    novo_poder_ataque = poder_ataque_base * (2 ** nivel_atual) if poder_ataque_base else 0
    nova_resistencia = resistencia_base * (2 ** nivel_atual) if resistencia_base else 0
    novo_saikoki = saikoki_base * (2 ** nivel_atual)

    novo_poder_ataque_formatado = f"{novo_poder_ataque:,}".replace(".", ",") if poder_ataque_base else "0"
    nova_resistencia_formatada = f"{nova_resistencia:,}".replace(".", ",") if resistencia_base else "0"
    novo_saikoki_formatado = f"{novo_saikoki:,}".replace(".", ",")

    card_atualizado = tecnica["card"]
    if poder_ataque_base:
        card_atualizado = re.sub(r'Attack☆Power:\(🔴[\d,]+%', f'Attack☆Power:(🔴{novo_poder_ataque_formatado}%', card_atualizado)
    if resistencia_base:
        card_atualizado = re.sub(r'Resistance:\(🟢[\d,]+%', f'Resistance:(🟢{nova_resistencia_formatada}%', card_atualizado)
    card_atualizado = re.sub(r'Saikōki☆Used:\(🔵[\d,]+%', f'Saikōki☆Used:(🔵{novo_saikoki_formatado}%', card_atualizado)

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
