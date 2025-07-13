import sys
import mysql.connector
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]
escolhido = sys.argv[2].capitalize()  # Aquatyl, Ignisprout ou Florisprout

iniciais = {
    "Aquatyl": {"requisito_id": 78},
    "Ignisprout": {"requisito_id": 91},
    "Florisprout": {"requisito_id": 164}
}

if escolhido not in iniciais:
    print("❌ Aeternal inválido. Escolha entre: Aquatyl, Ignisprout ou Florisprout.")
    sys.exit()

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True
)
cursor = conexao.cursor(dictionary=True)

try:
    # Buscar jogador
    cursor.execute("SELECT numero_registro FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador = cursor.fetchone()
    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    jogador_id = jogador['numero_registro']

    # Verificar se o jogador já possui um Aeternal inicial ou evolução
    cursor.execute("SELECT id_aeternal FROM jogador_aeternals WHERE id_jogador = %s", (jogador_id,))
    ids_aeternals = [a['id_aeternal'] for a in cursor.fetchall()]

    if ids_aeternals:
        query_base = "SELECT nome, base FROM aeternals WHERE id IN (%s)" % ",".join(["%s"] * len(ids_aeternals))
        cursor.execute(query_base, tuple(ids_aeternals))
        resultados = cursor.fetchall()
        for r in resultados:
            if r['base'] in iniciais or r['nome'] in iniciais:
                print(f"❌ Você já possui um Aeternal inicial ou uma evolução dele: {r['nome']}")
                sys.exit()

    # Buscar ID do Aeternal escolhido
    cursor.execute("SELECT id FROM aeternals WHERE nome = %s", (escolhido,))
    aeternal = cursor.fetchone()
    if not aeternal:
        print("❌ Aeternal não encontrado na base de dados.")
        sys.exit()

    # Associar Aeternal ao jogador
    vida_inicial = 300
    cursor.execute("""
        INSERT INTO jogador_aeternals (id_jogador, id_aeternal, vida)
        VALUES (%s, %s, %s)
    """, (jogador_id, aeternal['id'], vida_inicial))

    # Adicionar requisito específico do Aeternal
    requisito_id = iniciais[escolhido]["requisito_id"]
    cursor.execute("""
        INSERT INTO jogadores_requisitos (jogadores_id, requisito_id)
        VALUES (%s, %s)
    """, (jogador_id, requisito_id))

    # Adicionar requisito 62 (Eternal Ring)
    cursor.execute("""
        INSERT INTO jogadores_requisitos (jogadores_id, requisito_id)
        VALUES (%s, %s)
    """, (jogador_id, 62))

    conexao.commit()

    # Enviar imagem
    img_path = f"/home/root/img/{escolhido}.png"
    if os.path.exists(img_path):
        print(f"[imagem]{img_path}")

    # Mensagem final
    print(f"✅ {escolhido} foi adicionado com sucesso ao seu time! 🐾")
    print(f"🎉 Agora você pode começar sua jornada com {escolhido} ao seu lado!")
    print(f"🎉 Não esqueça de comprar na loja a técnica de invocação do seu aeternal através do seu eternal ring!")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")
finally:
    cursor.close()
    conexao.close()
