import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
requisito_nome = sys.argv[2] if len(sys.argv) > 2 else None

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
cursor = conexao.cursor(dictionary=True)

try:
    # Obter o ID do jogador e a classe
    cursor.execute("SELECT numero_registro, classe FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    jogador_id = jogador['numero_registro']
    classe_jogador = jogador['classe'].split(' ')[1]  # Remove "Classe " do valor

    # Obter os requisitos do jogador
    cursor.execute("SELECT requisito_id FROM jogadores_requisitos WHERE jogadores_id = %s", (jogador_id,))
    requisitos_jogador = [req['requisito_id'] for req in cursor.fetchall()]

    # Obter os nomes dos requisitos
    cursor.execute("SELECT id, nome FROM requerimentos_tecnicas")
    requisitos_nomes = {req['id']: req['nome'] for req in cursor.fetchall()}

    if requisito_nome:
        # Exibir técnicas para um requisito específico
        cursor.execute("SELECT id, nome FROM requerimentos_tecnicas WHERE nome = %s", (requisito_nome,))
        requisito = cursor.fetchone()

        if not requisito:
            print(" Requisito não encontrado.")
            sys.exit()

        if requisito['id'] not in requisitos_jogador:
            print(" Você não possui este requisito.")
            sys.exit()

        # Obter técnicas disponíveis e ainda não adquiridas
        cursor.execute("""
            SELECT t.id, t.nome, t.valor_zenis, t.classe
            FROM tecnicas t
            WHERE t.requerimento_id = %s
              AND FIELD(SUBSTRING(t.classe, 8), 'F', 'E', 'D', 'C', 'B', 'A') <= FIELD(%s, 'F', 'E', 'D', 'C', 'B', 'A')
              AND t.liberado = 1
              AND t.id NOT IN (SELECT tecnica_id FROM jogador_tecnicas WHERE jogador_registro = %s)
        """, (requisito['id'], classe_jogador, jogador_id))
        tecnicas_possiveis = cursor.fetchall()

        tecnicas_disponiveis = []

        for tecnica in tecnicas_possiveis:
            tecnica_id = tecnica['id']

            # Verificar se essa técnica possui requisitos adicionais de outras técnicas
            cursor.execute("""
                SELECT tecnica_requisito_id FROM tecnica_requisitos_tecnicas
                WHERE tecnica_id = %s
            """, (tecnica_id,))
            requisitos_tecnicos = [r['tecnica_requisito_id'] for r in cursor.fetchall()]

            if requisitos_tecnicos:
                # Verifica se o jogador possui TODAS as técnicas necessárias
                cursor.execute("""
                    SELECT tecnica_id FROM jogador_tecnicas
                    WHERE jogador_registro = %s
                """, (jogador_id,))
                tecnicas_jogador = [r['tecnica_id'] for r in cursor.fetchall()]

                if all(r in tecnicas_jogador for r in requisitos_tecnicos):
                    tecnicas_disponiveis.append(tecnica)
            else:
                tecnicas_disponiveis.append(tecnica)

        if not tecnicas_disponiveis:
            print(" Não há técnicas disponíveis para este requisito.")
            sys.exit()

        mensagem_mercado = f"*🛒Técnicas disponíveis para {requisito['nome']}🛒*\n\n"
        for tecnica in tecnicas_disponiveis:
            mensagem_mercado += f"✅ *{tecnica['nome']}* - 💰 {tecnica['valor_zenis']} Zenis\n"

        mensagem_mercado += "\n💰 Para comprar uma técnica, utilize o comando:\n*Comprar [nome da técnica]*\n\n💡 Certifique-se de ter Zenis suficientes antes de realizar a compra!\n\n*Se precisar de mais informações, estou aqui para ajudar! 💪*"

    else:
        # Exibir categorias disponíveis
        categorias_jogador = []
        for req_id in requisitos_jogador:
            cursor.execute("SELECT nome FROM requerimentos_tecnicas WHERE id = %s", (req_id,))
            requisito_nome = cursor.fetchone()['nome']
            categorias_jogador.append(requisito_nome)

        mensagem_mercado = "*🛒Mercado de Técnicas🛒*\n\n*🔍Categorias disponíveis para você:* \n\n"
        for categoria in categorias_jogador:
            mensagem_mercado += f"*📜 {categoria}*\n"

        mensagem_mercado += "\n📌 Para visualizar as técnicas de uma categoria, utilize o comando:\n*Mercado [nome da categoria]*\n\n💡 Após escolher uma categoria, você verá as técnicas disponíveis para compra dentro dela!\n\n*Se precisar de mais informações, estou aqui para ajudar! 💪*"

    print(mensagem_mercado)

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()