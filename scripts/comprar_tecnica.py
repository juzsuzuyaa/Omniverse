import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
tecnica = sys.argv[2]

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

    # Corrigido: Remover vírgulas dos zenis do jogador
    cursor.execute("SELECT numero_registro, REPLACE(zenis, ',', '') AS zenis, classe FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    # Corrigido: Usar valor_zenis e requerimento_id
    cursor.execute("""
        SELECT id, REPLACE(valor_zenis, ',', '') AS valor_zenis, liberado, requerimento_id, classe, card FROM tecnicas 
        WHERE nome = %s
    """, (tecnica,))
    tecnica_info = cursor.fetchone()

    if not tecnica_info:
        print("❌ Técnica não encontrada.")
        sys.exit()

    if not tecnica_info['liberado']:
        print("*❌ Compra Não Concluída!*\n\n⚠️ Essa técnica ainda não está liberada para compra.\n\n*💡 Verifique outras técnicas disponíveis no mercado para expandir seu repertório!*")
        sys.exit()

    # Corrigido: Verificar classe da técnica usando um dicionário
    classe_ordem = {'F': 1, 'E': 2, 'D': 3, 'C': 4, 'B': 5, 'A': 6}
    # Corrigido: Remover prefixo "Classe" e usar dicionário para comparação
    if classe_ordem[tecnica_info['classe'].split(' ')[1]] > classe_ordem[jogador['classe'].split(' ')[1]]:
        print("*❌ Compra Não Concluída!*\n\n⚠️ Você não pode comprar técnicas de classe superior.\n\n*💡 Verifique outras técnicas disponíveis no mercado para expandir seu repertório!*")
        sys.exit()

    # Verificar requisitos especiais (requerimento_id)
    if tecnica_info['requerimento_id']:
        cursor.execute("""
            SELECT 1 FROM jogadores_requisitos 
            WHERE jogadores_id = %s AND requisito_id = %s
        """, (jogador['numero_registro'], tecnica_info['requerimento_id']))
        requisito_especial = cursor.fetchone()
        if not requisito_especial:
            print("*❌ Compra Não Concluída!*\n\n⚠️ Você não possui os requisitos especiais para essa técnica.\n\n*💡 Verifique outras técnicas disponíveis no mercado para expandir seu repertório!*")
            sys.exit()

    # Verificar requisitos de outras técnicas
    cursor.execute("""
        SELECT tecnica_requisito_id 
        FROM tecnica_requisitos_tecnicas 
        WHERE tecnica_id = %s
    """, (tecnica_info['id'],))
    requisitos_tecnicas = cursor.fetchall()

    for req in requisitos_tecnicas:
        cursor.execute("""
            SELECT 1 FROM jogador_tecnicas 
            WHERE jogador_registro = %s AND tecnica_id = %s
        """, (jogador['numero_registro'], req['tecnica_requisito_id']))
        possui_tecnica = cursor.fetchone()
        if not possui_tecnica:
            print("*❌ Compra Não Concluída!*\n\n⚠️ Você não possui todas as técnicas necessárias para adquirir essa técnica.\n\n*💡 Verifique os pré-requisitos dessa técnica no mercado.*")
            sys.exit()

    # Corrigido: Verificar se a técnica já foi comprada
    cursor.execute("SELECT 1 FROM jogador_tecnicas WHERE jogador_registro = %s AND tecnica_id = %s",
                   (jogador['numero_registro'], tecnica_info['id']))
    tecnica_comprada = cursor.fetchone()
    if tecnica_comprada:
        print("*❌ Compra Não Concluída!*\n\n⚠️ Você já possui essa técnica em seu arsenal.\n\n*💡 Verifique outras técnicas disponíveis no mercado para expandir seu repertório!*")
        sys.exit()

    if int(jogador['zenis']) < int(tecnica_info['valor_zenis']):
        print("*❌ Compra Não Concluída!*\n\n⚠️ Você não possui zenis suficientes para comprar essa técnica.\n\n*💡 Verifique outras técnicas disponíveis no mercado para expandir seu repertório!*")
    else:
        novo_saldo = int(jogador['zenis']) - int(tecnica_info['valor_zenis'])
        novo_saldo_formatado = "{:,}".format(novo_saldo)
        cursor.execute("UPDATE jogadores SET zenis = %s WHERE numero_registro = %s", (novo_saldo, jogador['numero_registro']))
        cursor.execute("INSERT INTO jogador_tecnicas (jogador_registro, tecnica_id, nivel_upgrade) VALUES (%s, %s, 0)", 
                       (jogador['numero_registro'], tecnica_info['id']))
        cursor.execute("INSERT INTO logs (id_jogador, acao, detalhes) VALUES (%s, 'compra', %s)", 
                       (jogador['numero_registro'], f'Comprou {tecnica}. Saldo restante: {novo_saldo_formatado} Zenis'))
        conexao.commit()
        # Envia o card da técnica com uma quebra de linha no final
        print(tecnica_info['card'])

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()