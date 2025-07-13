import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
status = sys.argv[2]  # "vida", "saikoki" ou "forca"
quantidade = int(sys.argv[3])
tipo_moeda = sys.argv[4] if len(sys.argv) > 4 else None  # Novo argumento para tipo de moeda

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
cursor = conexao.cursor(dictionary=True)
try:
    # Verificar se o mercado está aberto
    cursor.execute("SELECT aberto_fechado FROM mercado WHERE id = 1")
    mercado = cursor.fetchone()

    if not mercado or mercado['aberto_fechado'] == 0:
        print("*❌ Compra Não Concluída!*\n\n⚠️ O mercado está fechado no momento.\n\n*Volte quando o mercado estiver aberto para expandir seu repertório!*")
        sys.exit()
    cursor.execute("SELECT numero_registro, moedas_treino, vida, saikoki, forca, rank_F_moeda_evolucao, rank_E_moeda_evolucao, rank_D_moeda_evolucao, rank_C_moeda_evolucao, rank_B_moeda_evolucao, rank_A_moeda_evolucao FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    if status == "forca" or status == "força":
        # Defina os valores de aumento e custo para cada item de força
        itens_forca = {
            "K": {"aumento": 2, "custo": 20},
        }

        if tipo_moeda.upper() not in itens_forca:
            print("❌ Item de força inválido.")
            sys.exit()

        aumento_forca = itens_forca[tipo_moeda.upper()]["aumento"]
        custo_total = quantidade * itens_forca[tipo_moeda.upper()]["custo"]

        if int(jogador['moedas_treino'].replace(',', '')) < custo_total:
            print(f"❌ Moedas de treino insuficientes. Você precisa de {custo_total} moedas.")
            sys.exit()

        limite_forca = int(jogador['vida']) * 0.04
        cursor.execute("SELECT forca FROM jogadores WHERE numero_registro = %s", (jogador['numero_registro'],))
        atual_forca = cursor.fetchone()['forca']
        if atual_forca + (aumento_forca * quantidade) > limite_forca:
            print("❌ Você atingiu o limite de força permitido.\n\n*💪 Limite permitido: {} KG*".format(limite_forca))
            sys.exit()

        try:
            nova_forca = atual_forca + (aumento_forca * quantidade)
            cursor.execute("UPDATE jogadores SET forca = %s, moedas_treino = %s WHERE numero_registro = %s", (nova_forca, int(jogador['moedas_treino']) - custo_total, jogador['numero_registro']))
            cursor.execute("INSERT INTO logs (id_jogador, acao, detalhes) VALUES (%s, 'upgrade', %s)", (jogador['numero_registro'], f"Upou {quantidade} força com o item {tipo_moeda.upper()}. Força resultante: {nova_forca}"))
            conexao.commit()
            print("*✅ Aprimoramento de Força Concluído!*\n\n *💪 Força aumentada em +{} KG*\n️ 🎟️ *Moedas de Treino restantes: {}*".format(quantidade * aumento_forca, int(jogador['moedas_treino'].replace(',', '')) - custo_total))
        except Exception as e:
            print(f"Erro ao atualizar força: {e}")

    elif status in ["vida", "saikoki", "saikōki"]:
        if not tipo_moeda:
            print("❌ Tipo de moeda não especificado.")
            sys.exit()

        moedas = {
            "F": jogador['rank_F_moeda_evolucao'],
            "E": jogador['rank_E_moeda_evolucao'],
            "D": jogador['rank_D_moeda_evolucao'],
            "C": jogador['rank_C_moeda_evolucao'],
            "B": jogador['rank_B_moeda_evolucao'],
            "A": jogador['rank_A_moeda_evolucao']
        }
        
        aumento = {
            "F": 100,
            "E": 1000,
            "D": 10000,
            "C": 100000,
            "B": 1000000,
            "A": 10000000
        }

        if moedas[tipo_moeda.upper()] < quantidade:
            print(f"❌ Você não possui *Moedas de Rank {tipo_moeda.upper()}* suficientes para realizar esse aprimoramento.")
            sys.exit()
            
        if status == 'saikōki':
            status = 'saikoki'

        if status == "saikoki" or status == "saikōki":
            limite_saikoki = int(jogador['vida']) * 5
            nova_saikoki = int(jogador['saikoki'].replace(',', '')) + (aumento[tipo_moeda.upper()] * quantidade)
            if nova_saikoki > limite_saikoki:
                print("❌ Você atingiu o limite de saikōki permitido.")
                sys.exit()

        else: # vida
            nova_vida = int(jogador['vida']) + (aumento[tipo_moeda.upper()] * quantidade)

        cursor.execute("UPDATE jogadores SET " + status + " = %s, rank_" + tipo_moeda.lower() + "_moeda_evolucao = rank_" + tipo_moeda.lower() + "_moeda_evolucao - %s WHERE numero_registro = %s", (nova_vida if status == "vida" else nova_saikoki, quantidade, jogador['numero_registro']))
        # Buscar nickname do jogador
    cursor.execute("SELECT nickname FROM jogadores WHERE numero_registro = %s", (jogador['numero_registro'],))
    nickname = cursor.fetchone()['nickname']

    # Buscar saldo atual de moedas de evolução e moedas de treino
    cursor.execute("""
        SELECT moedas_treino, rank_F_moeda_evolucao, rank_E_moeda_evolucao, rank_D_moeda_evolucao,
            rank_C_moeda_evolucao, rank_B_moeda_evolucao, rank_A_moeda_evolucao
        FROM jogadores WHERE numero_registro = %s
    """, (jogador['numero_registro'],))
    saldos = cursor.fetchone()

    # Definir saldo final das moedas e TC
    moeda_restante = saldos[f'rank_{tipo_moeda.upper()}_moeda_evolucao'] if status in ["vida", "saikoki", "saikōki"] else "N/A"
    tc_restante = saldos['moedas_treino']
    # Buscar valores atualizados de vida, saikoki e forca
    cursor.execute("SELECT vida, saikoki, forca FROM jogadores WHERE numero_registro = %s", (jogador['numero_registro'],))
    valores_atualizados = cursor.fetchone()
    vida_atualizada = valores_atualizados['vida']
    saikoki_atualizado = valores_atualizados['saikoki']
    forca_atualizada = valores_atualizados['forca']

    # Excluir registros antigos do mesmo jogador e tipo de ação
    cursor.execute("DELETE FROM logs WHERE id_jogador = %s AND acao = 'upgrade'", (jogador['numero_registro'],))

    # Criar mensagem do log com os valores atualizados
    detalhes_log = f"{nickname} aumentou seus atributos para {int(vida_atualizada):,}, {int(saikoki_atualizado):,}, {int(forca_atualizada):,}. " \
                f"Saldo restante: Moeda[{tipo_moeda.upper()}] {moeda_restante if moeda_restante == 'N/A' else moeda_restante}, {int(tc_restante):,} TC"


    # Inserir novo log
    cursor.execute("INSERT INTO logs (id_jogador, acao, detalhes) VALUES (%s, 'upgrade', %s)", 
                (jogador['numero_registro'], detalhes_log))

    conexao.commit()

        # Mensagens de sucesso para vida e saikoki
    if status == "vida":
            print("*✅ Aprimoramento de Vida Concluído!*\n\n*❤️ Vida aumentada em +{}*\n️ *🎟️ Moedas de Evolução {} restantes: {}*".format(quantidade * aumento[tipo_moeda.upper()], tipo_moeda.upper(), moedas[tipo_moeda.upper()] - quantidade))
    elif status == "saikoki" or status == "saikōki":
            print("*✅ Aprimoramento de Saikōki Concluído!*\n\n*🔷 Saikōki aumentado em +{}*\n️ *🎟️ Moedas de Evolução {} restantes: {}*".format(quantidade * aumento[tipo_moeda.upper()], tipo_moeda.upper(), moedas[tipo_moeda.upper()] - quantidade))
finally:
    cursor.close()
    conexao.close()