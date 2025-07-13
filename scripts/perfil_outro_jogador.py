import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

nome_jogador = sys.argv[1]

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True
)
cursor = conexao.cursor(dictionary=True)

try:
    cursor.execute("""
        SELECT nickname, vida, saikoki, forca, zenis, moedas_treino, 
            rank_F_moeda_evolucao, rank_E_moeda_evolucao, rank_D_moeda_evolucao, 
            rank_C_moeda_evolucao, rank_B_moeda_evolucao, rank_A_moeda_evolucao, 
            rank_F_missoes, rank_E_missoes, rank_D_missoes, 
            rank_C_missoes, rank_B_missoes, rank_A_missoes, v_d
        FROM jogadores 
        WHERE nickname = %s
    """, (nome_jogador,))
    
    jogador = cursor.fetchone()

    if not jogador:
        print(f"❌ Jogador com nome '{nome_jogador}' não encontrado.")
        sys.exit()

    moedas_evolucao = f"F: {int(jogador['rank_F_moeda_evolucao']):,}, E: {int(jogador['rank_E_moeda_evolucao']):,}, D: {int(jogador['rank_D_moeda_evolucao']):,}, C: {int(jogador['rank_C_moeda_evolucao']):,}, B: {int(jogador['rank_B_moeda_evolucao']):,}, A: {int(jogador['rank_A_moeda_evolucao']):,}"
    missoes_concluidas = f"F: {int(jogador['rank_F_missoes']):,}, E: {int(jogador['rank_E_missoes']):,}, D: {int(jogador['rank_D_missoes']):,}, C: {int(jogador['rank_C_missoes']):,}, B: {int(jogador['rank_B_missoes']):,}, A: {int(jogador['rank_A_missoes']):,}"

    perfil = f""" *🔍Perfil do Jogador 🔍*

Nickname: *{jogador['nickname']}*
    •   *Vida:* {int(jogador['vida']):,}
    •   *Saikōki:* {int(jogador['saikoki']):,}
    •   *Força:* {int(jogador['forca']):,} KG
    •   *Zenis:* {int(jogador['zenis']):,}
    •   *Moedas de Treino:* {int(jogador['moedas_treino']):,}
    •   *Moeda de Evolução:* {moedas_evolucao}
    •   *Missões Concluídas:* {missoes_concluidas}
    •   *Vitórias & Derrotas:* {jogador['v_d']}

⚔️ Continue acompanhando seus rivais! ⚔️
"""

    print(perfil)

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    cursor.close()
    conexao.close()
