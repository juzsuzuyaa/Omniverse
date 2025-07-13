import io
import sys
import mysql.connector
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    if len(sys.argv) < 4:
        print("Uso: python3 upar_tecnicas.py [numero_whatsapp] [nome_tecnica] [quantidade (opcional)]", file=sys.stderr)
        sys.exit(1)

    numero_whatsapp = sys.argv[1]
    nome_tecnica = sys.argv[2]
    quantidade = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
    cursor = conexao.cursor(dictionary=True)
    # Verificar se o mercado está aberto
    cursor.execute("SELECT aberto_fechado FROM mercado WHERE id = 1")
    mercado = cursor.fetchone()

    if not mercado or mercado['aberto_fechado'] == 0:
        print("*❌ Compra Não Concluída!*\n\n⚠️ O mercado está fechado no momento.\n\n*Volte quando o mercado estiver aberto para expandir seu repertório!*")
        sys.exit()
    cursor.execute("SELECT numero_registro, moedas_treino, saikoki FROM jogadores WHERE numero_whatsapp = %s", (numero_whatsapp,))
    jogador = cursor.fetchone()

    if not jogador:
        print("Jogador não encontrado.", file=sys.stderr)
        sys.exit(1)

    jogador_registro = jogador["numero_registro"]
    moedas_treino = int(jogador["moedas_treino"].replace(',', ''))
    saikoki_jogador = int(jogador["saikoki"].replace(',', ''))

    cursor.execute("""
        SELECT jt.nivel_upgrade, t.id AS tecnica_id, t.nome, t.saikoki_usado, t.poder_ataque, t.resistencia, t.aprimoravel, t.card
        FROM jogador_tecnicas jt
        JOIN tecnicas t ON jt.tecnica_id = t.id
        WHERE jt.jogador_registro = %s AND LOWER(t.nome) = %s
    """, (jogador_registro, nome_tecnica.lower()))
    tecnica = cursor.fetchone()

    if not tecnica:
        print("Técnica não encontrada para este jogador.", file=sys.stderr)
        sys.exit(1)

    if tecnica["aprimoravel"] == 0:
        print(f"A técnica '{nome_tecnica}' não pode ser aprimorada.", file=sys.stderr)
        sys.exit(1)

    nivel_atual = tecnica["nivel_upgrade"]
    poder_ataque_base = int(tecnica["poder_ataque"].replace(',', '')) if tecnica["poder_ataque"] else 0
    resistencia_base = int(tecnica["resistencia"].replace(',', '')) if tecnica["resistencia"] else 0
    saikoki_base = int(tecnica["saikoki_usado"].replace(',', ''))

    novo_nivel = nivel_atual + quantidade
    novo_poder_ataque = poder_ataque_base * (2 ** novo_nivel) if poder_ataque_base else 0
    nova_resistencia = resistencia_base * (2 ** novo_nivel) if resistencia_base else 0
    novo_saikoki = saikoki_base * (2 ** novo_nivel)

    #if novo_poder_ataque > 25000:
        #print(
    #"❌ Upgrade Não Concluído!\n\n"
    #f"⚠️ O upgrade levaria o poder de ataque para {novo_poder_ataque:,}, ultrapassando o limite de 25,000 do sino de prata.\n\n"
    #"🔋 *Requisito Necessário:*\n"
    #"    • É necessário aguardar um novo item para que o upgrade seja concluído.\n\n"
    #"📢 *Dica:*\n"
    #"    • A cada upgrade, o custo de Saikōki da técnica *dobra* ⚡.\n"
    #"    • Certifique-se de ter energia suficiente antes de tentar novamente!\n\n"
    #"💡 *Considere aumentar seu Saikōki antes de realizar o upgrade!* 🚀"
#)

        #sys.exit(1)

    #if nova_resistencia > 25000:
        #print(
    #"❌ Upgrade Não Concluído!\n\n"
    #f"⚠️ O upgrade levaria a resistência para {nova_resistencia:,}, ultrapassando o limite de 25,000 do sino de prata.\n\n"
    #"🔋 *Requisito Necessário:*\n"
    #"    • É necessário aguardar um novo item para que o upgrade seja concluído.\n\n"
    #"📢 *Dica:*\n"
    #"    • A cada upgrade, o custo de Saikōki da técnica *dobra* ⚡.\n"
    #"    • Certifique-se de ter energia suficiente antes de tentar novamente!\n\n"
    #"💡 *Considere aumentar seu Saikōki antes de realizar o upgrade!* 🚀"
#)
        #sys.exit(1)

    if novo_saikoki > saikoki_jogador:
        print(
    "❌ Upgrade Não Concluído!\n\n"
    "⚠️ Você não possui Saikōki suficiente para utilizar essa técnica após o aprimoramento.\n\n"
    "🔋 *Requisito Necessário:*\n"
    f"    • É necessário possuir *{novo_saikoki:,}* de Saikōki para que o upgrade seja concluído.\n\n"
    "📢 *Dica:*\n"
    "    • A cada upgrade, o custo de Saikōki da técnica *dobra* ⚡.\n"
    "    • Certifique-se de ter energia suficiente antes de tentar novamente!\n\n"
    "💡 *Considere aumentar seu Saikōki antes de realizar o upgrade!* 🚀"
)
        sys.exit(1)

    custo_total = 0
    for i in range(nivel_atual + 1, novo_nivel + 1):
        dano_ataque = poder_ataque_base * (2 ** i)
        dano_resistencia = resistencia_base * (2 ** i)
    if dano_ataque > 250000 or dano_resistencia > 250000:
        print(f"❌ Upgrade não permitido: ultrapassaria o limite de 250.000.", file=sys.stderr)
        sys.exit(1)
    if dano_ataque > 25000 or dano_resistencia > 25000:
        custo_total += 1000
    else:
        custo_total += 100

    if moedas_treino < custo_total:
        print(f"Moedas de treino insuficientes. Você tem {moedas_treino:,}, mas precisa de {custo_total:,}.", file=sys.stderr)
        sys.exit(1)

    cursor.execute("""
        UPDATE jogador_tecnicas 
        SET nivel_upgrade = %s 
        WHERE jogador_registro = %s AND tecnica_id = %s
    """, (novo_nivel, jogador_registro, tecnica["tecnica_id"]))

    cursor.execute("""
        UPDATE jogadores 
        SET moedas_treino = %s 
        WHERE numero_registro = %s
    """, (moedas_treino - custo_total, jogador_registro))

    # Obter o nível atual da técnica
    cursor.execute("SELECT nivel_upgrade FROM jogador_tecnicas WHERE jogador_registro = %s AND tecnica_id = %s", (jogador_registro, tecnica["tecnica_id"]))
    tecnica_jogador = cursor.fetchone()
    novo_nivel = tecnica_jogador['nivel_upgrade'] - 1 + quantidade if tecnica_jogador else quantidade

    #obter o saldo atual de moedas de treino
    cursor.execute("SELECT moedas_treino FROM jogadores WHERE numero_registro = %s", (jogador_registro,))
    saldo = cursor.fetchone()
    saldo = saldo['moedas_treino']
    saldo = f"{saldo}".replace(",", ".")
    saldo = int(saldo)

    # Excluir registros antigos do mesmo jogador e tecnica
    cursor.execute("DELETE FROM logs WHERE id_jogador = %s AND id_tecnica = %s", (jogador['numero_registro'], tecnica["tecnica_id"]))

    # Atualizar o registro de log
    cursor.execute("""
        INSERT INTO logs (id_jogador, acao, detalhes, id_tecnica) VALUES (%s, 'upgrade_tecnica', %s, %s)
    """, (jogador_registro, f"Técnica {tecnica['nome']} está atualmente com {novo_nivel} ups. Saldo restante {saldo:,} TC", tecnica["tecnica_id"]))
    conexao.commit()

    novo_poder_ataque_formatado = f"{novo_poder_ataque:,}".replace(".", ",") if poder_ataque_base else "0"
    nova_resistencia_formatada = f"{nova_resistencia:,}".replace(".", ",") if resistencia_base else "0"
    novo_saikoki_formatado = f"{novo_saikoki:,}".replace(".", ",")

    card_atualizado = tecnica["card"]
    if poder_ataque_base:
        card_atualizado = re.sub(r'Attack☆Power:\(🔴[\d,]+%', f'Attack☆Power:(🔴{novo_poder_ataque_formatado}%', card_atualizado)
    if resistencia_base:
        card_atualizado = re.sub(r'Resistance:\(🟢[\d,]+%', f'Resistance:(🟢{nova_resistencia_formatada}%', card_atualizado)
    card_atualizado = re.sub(r'Saikōki☆Used:\(🔵[\d,]+%', f'Saikōki☆Used:(🔵{novo_saikoki_formatado}%', card_atualizado)
    card_atualizado = re.sub(r'Up☆Force:\(🟢[\d,]+%', f'Up☆Force:(🟢{novo_poder_ataque_formatado}%', card_atualizado)

    # Mensagem de confirmação do upgrade
    mensagem_confirmacao = f"Técnica {tecnica['nome']} melhorada com sucesso!\n"
    if poder_ataque_base:
        mensagem_confirmacao += f"Novo poder de ataque: {novo_poder_ataque_formatado}\n"
    if resistencia_base:
        mensagem_confirmacao += f"Nova resistência: {nova_resistencia_formatada}\n"
    mensagem_confirmacao += f"Novo consumo de saikoki: {novo_saikoki_formatado}\n"
    mensagem_confirmacao += f"Moedas restantes: {f'{moedas_treino - custo_total:,}'.replace(',', '.')}\n"

    # Mensagem do card atualizado
    mensagem_card = card_atualizado

    # Imprimir as mensagens separadamente
    sys.stdout.write(mensagem_card)

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
