import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2]
tecnica = sys.argv[3]
upgrades = int(sys.argv[4]) if len(sys.argv) > 4 else 0  # Padrão: 0 upgrades

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

    if not jogador_admin or not jogador_admin['administrador']:
        print("❌ Você não tem permissão para associar técnicas.")
        sys.exit()

    # Buscar o jogador pelo nickname
    cursor.execute("SELECT numero_registro FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    # Buscar a técnica pelo nome e seus valores base
    cursor.execute("SELECT id, saikoki_usado, poder_ataque, resistencia FROM tecnicas WHERE nome = %s", (tecnica,))
    tecnica_info = cursor.fetchone()

    if not tecnica_info:
        print("❌ Técnica não encontrada.")
        sys.exit()

    # Verificar se o jogador já possui essa técnica
    cursor.execute("""
        SELECT 1 FROM jogador_tecnicas 
        WHERE jogador_registro = %s AND tecnica_id = %s
    """, (jogador['numero_registro'], tecnica_info['id']))
    ja_possui = cursor.fetchone()

    if ja_possui:
        print(f"⚠️ {nickname} já possui a técnica: {tecnica}. Nenhuma ação foi realizada.")
        sys.exit()

    # Converter valores para inteiro antes de calcular
    saikoki_base = int(tecnica_info['saikoki_usado']) if tecnica_info['saikoki_usado'] else 0
    poder_ataque_base = int(tecnica_info['poder_ataque']) if tecnica_info['poder_ataque'] else 0
    resistencia_base = int(tecnica_info['resistencia']) if tecnica_info['resistencia'] else 0

    # Calcular valores com base nos upgrades (dobrando a cada nível)
    saikoki_usado = saikoki_base * (2 ** upgrades)
    poder_ataque = poder_ataque_base * (2 ** upgrades)
    resistencia = resistencia_base * (2 ** upgrades)

    # Formatar números para exibição (com vírgula separando milhares)
    saikoki_formatado = f"{saikoki_usado:,}".replace(",", ".")
    poder_ataque_formatado = f"{poder_ataque:,}".replace(",", ".")
    resistencia_formatada = f"{resistencia:,}".replace(",", ".")

    # Associar a técnica ao jogador na tabela jogador_tecnicas
    cursor.execute("""
        INSERT INTO jogador_tecnicas (jogador_registro, tecnica_id, nivel_upgrade) 
        VALUES (%s, %s, %s)
    """, (jogador['numero_registro'], tecnica_info['id'], upgrades))

    conexao.commit()

    # Mensagem formatada
    print(f"✅ Técnica Associada com Sucesso!\n")
    print(f"🎉 A técnica {tecnica} foi vinculada com sucesso a {nickname}!\n")
    print(f"📊 Detalhes da Técnica Adicionada:")
    print(f"⚡ Saikōki Usado: {saikoki_formatado}")
    print(f"💥 Poder de Ataque: {poder_ataque_formatado}")
    print(f"🛡️ Resistência: {resistencia_formatada}\n")
    print(f"🔥 Agora {nickname} pode utilizar essa técnica em batalha! 🚀")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    cursor.close()
    conexao.close()
