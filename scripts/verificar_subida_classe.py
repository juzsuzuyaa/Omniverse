import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Junta o nome e separa classe
nickname = ' '.join(sys.argv[1:-1])
nova_classe = sys.argv[-1].upper()

# Requisitos por classe
requisitos = {
    'E': {'vida': 2000, 'energia': 4000, 'forca': 80, 'ataque': {'qtd': 5, 'min': 800}, 'resistencia': {'qtd': 5, 'min': 800}},
    'D': {'vida': 20000, 'energia': 40000, 'forca': 800, 'ataque': {'qtd': 10, 'min': 8000}, 'resistencia': {'qtd': 10, 'min': 8000}},
    'C': {'vida': 200000, 'energia': 400000, 'forca': 8000, 'ataque': {'qtd': 10, 'min': 80000}, 'resistencia': {'qtd': 10, 'min': 80000}},
    'B': {'vida': 2000000, 'energia': 4000000, 'forca': 80000, 'ataque': {'qtd': 10, 'min': 800000}, 'resistencia': {'qtd': 10, 'min': 800000}},
    'A': {'vida': 20000000, 'energia': 40000000, 'forca': 800000, 'ataque': {'qtd': 10, 'min': 8000000}, 'resistencia': {'qtd': 10, 'min': 8000000}},
}

if nova_classe not in requisitos:
    print("❌ Classe informada inválida.")
    sys.exit()

try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="omniverse",
        ssl_disabled=True
    )
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT numero_registro, vida, saikoki, forca, classe FROM jogadores WHERE nickname = %s", (nickname,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    jogador_id = jogador['numero_registro']
    try:
        vida = int(str(jogador['vida']).replace(',', '').strip())
        saikoki = int(str(jogador['saikoki']).replace(',', '').strip())
        forca = int(str(jogador['forca']).replace(',', '').strip())
    except Exception as erro:
        print(f"Erro ao converter atributos do jogador: {erro}")
        sys.exit()

    classe_atual = jogador['classe'].split()[-1]

    if classe_atual == nova_classe:
        print(f"⚠️ {nickname} já pertence à Classe {nova_classe}.")
        sys.exit()

    req = requisitos[nova_classe]
    falhas = []

    if vida < req['vida']:
        falhas.append(f"• Vida atual: {vida:,} / {req['vida']:,}")
    if saikoki < req['energia']:
        falhas.append(f"• Energia atual: {saikoki:,} / {req['energia']:,}")
    if forca < req['forca']:
        falhas.append(f"• Força atual: {forca:,} KG / {req['forca']:,} KG")

    # Verificar técnicas
    cursor.execute("""
        SELECT t.nome, t.resistencia, t.poder_ataque, jt.nivel_upgrade
        FROM jogador_tecnicas jt
        JOIN tecnicas t ON jt.tecnica_id = t.id
        WHERE jt.jogador_registro = %s
        AND t.nome NOT LIKE 'Omni-King%%'
        AND t.nome NOT LIKE 'Aeternals%%'
        AND t.nome NOT LIKE 'Power-Up%%'
        AND t.fisico = 0
    """, (jogador_id,))
    tecnicas = cursor.fetchall()

    tecnicas_ataque = 0
    tecnicas_resistencia = 0

    for tecnica in tecnicas:
        try:
            nivel_up = int(str(tecnica['nivel_upgrade']).strip())
            base_poder = int(str(tecnica['poder_ataque']).replace(',', '').strip()) if tecnica['poder_ataque'] is not None else 0
            base_resistencia = int(str(tecnica['resistencia']).replace(',', '').strip()) if tecnica['resistencia'] is not None else 0
        except Exception as erro:
            print(f"Erro ao processar técnica '{tecnica['nome']}': {erro}")
            sys.exit()

        mult = 2 ** nivel_up
        poder_total = base_poder * mult
        resistencia_total = base_resistencia * mult

        if poder_total >= req['ataque']['min']:
            tecnicas_ataque += 1
        if resistencia_total >= req['resistencia']['min']:
            tecnicas_resistencia += 1

    if tecnicas_ataque < req['ataque']['qtd']:
        falhas.append(f"• Técnicas de ataque válidas: {tecnicas_ataque}/{req['ataque']['qtd']} com {req['ataque']['min']:,}+")
    if tecnicas_resistencia < req['resistencia']['qtd']:
        falhas.append(f"• Técnicas de resistência válidas: {tecnicas_resistencia}/{req['resistencia']['qtd']} com {req['resistencia']['min']:,}+")

    if nova_classe in ['C', 'B', 'A']:
        cursor.execute("""
            SELECT requisito_id FROM jogadores_requisitos
            WHERE jogadores_id = %s AND requisito_id IN (2, 3, 4, 5, 6)
        """, (jogador_id,))
        manipulacoes = set(r['requisito_id'] for r in cursor.fetchall())
        manipulacoes_necessarias = {2, 3, 4, 5, 6}

        if not manipulacoes_necessarias.issubset(manipulacoes):
            faltando = manipulacoes_necessarias - manipulacoes
            nomes = {
                2: "Água", 3: "Terra", 4: "Fogo", 5: "Ar", 6: "Relâmpago"
            }
            faltam_texto = ', '.join(f"*{nomes[i]}*" for i in faltando)
            falhas.append(f"• Faltam manipulações elementares: {faltam_texto}")

    if falhas:
        print(f"❌ *{nickname} ainda não atende aos requisitos para subir para Classe {nova_classe}:*\n\n" + "\n".join(falhas))
    else:
        print(f"✅ *Parabéns, {nickname} pode subir para Classe {nova_classe} com sucesso!*")


except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    if cursor: cursor.close()
    if conexao and conexao.is_connected(): conexao.close()
