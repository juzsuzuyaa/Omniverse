import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
nickname = sys.argv[2]
rank = sys.argv[3].upper()  # Garante que o rank esteja em maiúsculo
quantidade = int(sys.argv[4])

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
        print("❌ Você não tem permissão para marcar missões concluídas.")
        sys.exit()

    # Buscar o jogador pelo nickname
    cursor.execute("""
        SELECT numero_registro, moedas_treino, zenis, rank_F_missoes, rank_E_missoes, rank_D_missoes,
               rank_C_missoes, rank_B_missoes, rank_A_missoes, rank_F_moeda_evolucao, rank_E_moeda_evolucao,
               rank_D_moeda_evolucao, rank_C_moeda_evolucao, rank_B_moeda_evolucao, rank_A_moeda_evolucao
        FROM jogadores WHERE nickname = %s
    """, (nickname,))
    
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    coluna_rank_missao = f"rank_{rank}_missoes"  # Nome da coluna para o rank especificado
    coluna_rank_moeda = f"rank_{rank}_moeda_evolucao"  # Nome da coluna para moedas de evolução
    saldo_atual_missao = jogador[coluna_rank_missao]
    saldo_atual_moeda = jogador[coluna_rank_moeda]

    novo_saldo_missao = saldo_atual_missao + quantidade
    novo_saldo_moeda = saldo_atual_moeda + quantidade

    # Recompensas por rank
    recompensas = {
        "F": {"zenis": 3000, "tc": 100},
        "E": {"zenis": 6000, "tc": 200},
        "D": {"zenis": 18000, "tc": 600},
        "C": {"zenis": 24000, "tc": 800},
        "B": {"zenis": 48000, "tc": 1600},
        "A": {"zenis": 96000, "tc": 3200}
    }

    zenis_ganhos = recompensas[rank]["zenis"] * quantidade
    tc_ganhos = recompensas[rank]["tc"] * quantidade

    # Conversão de moedas para int antes da soma
    tc_atual = int(jogador['moedas_treino'].replace(',', '')) if jogador['moedas_treino'] else 0
    zenis_atual = int(jogador['zenis'].replace(',', '')) if jogador['zenis'] else 0

    novo_tc = tc_atual + tc_ganhos
    novo_zenis = zenis_atual + zenis_ganhos

    # Atualizar os valores no banco
    cursor.execute(f"""
        UPDATE jogadores 
        SET {coluna_rank_missao} = %s, {coluna_rank_moeda} = %s, moedas_treino = %s, zenis = %s 
        WHERE numero_registro = %s
    """, (novo_saldo_missao, novo_saldo_moeda, str(novo_tc), str(novo_zenis), jogador['numero_registro']))

    conexao.commit()

    print(f"✅ Missões de Rank {rank} marcadas com sucesso para {nickname}!\n\n"
          f"Zenis ganhos: {zenis_ganhos:,}\n"
          f"Training Coins ganhos: {tc_ganhos:,}\n"
          f"Moedas de Evolução de rank {rank} ganhas: {quantidade}")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()
