import io
import sys
import mysql.connector

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    if len(sys.argv) < 4:
        print("Uso: python3 upar_aeternal.py [numero_whatsapp] [nome_aeternal] [quantidade] [tipo_doce]", file=sys.stderr)
        sys.exit(1)

    numero_whatsapp = sys.argv[1]
    nome_aeternal = sys.argv[2]
    quantidade = int(sys.argv[3])
    tipo_doce = sys.argv[4].lower() if len(sys.argv) >= 5 else "normal"

    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="omniverse",
        ssl_disabled=True
    )
    cursor = conexao.cursor(dictionary=True)

    # Verificar se o mercado está aberto
    cursor.execute("SELECT aberto_fechado FROM mercado WHERE id = 1")
    mercado = cursor.fetchone()

    if not mercado or mercado['aberto_fechado'] == 0:
        print("*❌ Compra Não Concluída!*\n\n⚠️ O mercado está fechado no momento.\n\n*Volte quando o mercado estiver aberto para expandir seu repertório!*")
        sys.exit()

    # Obter jogador
    cursor.execute("SELECT numero_registro, zenis, classe FROM jogadores WHERE numero_whatsapp = %s", (numero_whatsapp,))
    jogador = cursor.fetchone()
    if not jogador:
        print("Jogador não encontrado.", file=sys.stderr)
        sys.exit(1)

    jogador_id = jogador["numero_registro"]
    zenis_jogador = int(str(jogador["zenis"]).replace(",", ""))
    classe_jogador = jogador["classe"]

    # Definir regras do doce
    if tipo_doce == "super":
        # Verifica se é Classe D ou superior
        letra_classe = classe_jogador.replace("Classe ", "").upper()
        if letra_classe not in ["D", "C", "B", "A"]:
            print("❌ O *Super Candy* só pode ser usado por jogadores de *Classe D* ou superior.")
            sys.exit()
        ganho_vida = 1000
        custo_unitario = 4000
        nome_doce = "Super Candy"
    else:
        tipo_doce = "normal"
        ganho_vida = 100
        custo_unitario = 500
        nome_doce = "Normal Candy"

    # Obter Aeternal
    cursor.execute("SELECT id, vida, fase, base, minimo, maximo FROM aeternals WHERE nome = %s", (nome_aeternal,))
    aeternal = cursor.fetchone()
    if not aeternal:
        print("Aeternal não encontrado.")
        sys.exit()

    aeternal_id = aeternal["id"]
    aeternal_vida_base = aeternal["vida"]
    fase_atual = aeternal["fase"]
    base_aeternal = aeternal["base"]
    nivel_minimo = aeternal["minimo"]
    nivel_maximo = aeternal["maximo"]

    # Obter dados do jogador_aeternals
    cursor.execute("SELECT vida FROM jogador_aeternals WHERE id_jogador = %s AND id_aeternal = %s", (jogador_id, aeternal_id))
    jogador_aeternal = cursor.fetchone()
    if not jogador_aeternal:
        print("Jogador não possui este Aeternal.", file=sys.stderr)
        sys.exit(1)

    vida_atual = jogador_aeternal["vida"]
    nivel_atual = vida_atual // aeternal_vida_base

    if nivel_atual >= nivel_maximo:
        print(f"⚠️ Seu Aeternal {nome_aeternal} já está no nível máximo ({nivel_maximo}).")
        sys.exit()

    # Calcular upgrades possíveis
    limite_vida = nivel_maximo * aeternal_vida_base
    upgrades_disponiveis = (limite_vida - vida_atual) // ganho_vida
    quantidade_real = min(quantidade, upgrades_disponiveis)

    if quantidade_real == 0:
        print(f"⚠️ Seu Aeternal {nome_aeternal} já atingiu o nível máximo permitido ({nivel_maximo}).")
        sys.exit()

    nova_vida = vida_atual + (ganho_vida * quantidade_real)
    novo_nivel = nova_vida // aeternal_vida_base
    custo_total = custo_unitario * quantidade_real

    if zenis_jogador < custo_total:
        print(f"❌ Zenis insuficientes. Você precisa de {custo_total:,} Zenis.")
        sys.exit()

    mensagem = (f"✅ *Aprimoramento de Aeternal Concluído!*\n\n"
                f"🌀 *{nome_aeternal}* foi aprimorado com sucesso!\n\n"
                f"❤️ *Nova Vida:* {nova_vida:,}\n"
                f"📈 *Novo Nível:* {novo_nivel}\n"
                f"💰 *Zenis Gastos:* {custo_total:,}\n"
                f"💰 *Zenis Restantes:* {zenis_jogador - custo_total:,}\n"
                f"🍬 *Doce Utilizado:* {nome_doce}\n")

    # Verifica se deve evoluir para próxima fase
    if novo_nivel >= nivel_maximo:
        proxima_fase = fase_atual + 1

        cursor.execute("SELECT id, vida FROM aeternals WHERE base = %s AND fase = %s", (base_aeternal, proxima_fase))
        novo_aeternal = cursor.fetchone()

        if novo_aeternal:
            novo_aeternal_id = novo_aeternal["id"]
            nova_vida_base = novo_aeternal["vida"]
            nova_vida_evoluida = novo_nivel * nova_vida_base

            cursor.execute("UPDATE jogador_aeternals SET id_aeternal = %s, vida = %s WHERE id_jogador = %s AND id_aeternal = %s",
                           (novo_aeternal_id, nova_vida_evoluida, jogador_id, aeternal_id))

            mensagem += (f"\n🎉 *Parabéns!*\n\n"
                         f"🌀 Seu *{nome_aeternal}* atingiu o nível máximo e evoluiu para a próxima forma!\n"
                         f"🔥 *Agora ele está ainda mais poderoso!*\n"
                         f"❤️ *Nova Vida:* {nova_vida_evoluida:,}\n")
        else:
            cursor.execute("UPDATE jogador_aeternals SET vida = %s WHERE id_jogador = %s AND id_aeternal = %s",
                           (nova_vida, jogador_id, aeternal_id))
    else:
        cursor.execute("UPDATE jogador_aeternals SET vida = %s WHERE id_jogador = %s AND id_aeternal = %s",
                       (nova_vida, jogador_id, aeternal_id))

    # Atualizar zenis
    cursor.execute("UPDATE jogadores SET zenis = %s WHERE numero_registro = %s", (zenis_jogador - custo_total, jogador_id))

    # Registrar log
    cursor.execute("INSERT INTO logs (id_jogador, acao, detalhes, id_aeternal) VALUES (%s, 'aeternal', %s, %s)", 
                   (jogador_id, f"Vida do Aeternal {nome_aeternal} aprimorada para {nova_vida:,} usando {nome_doce}. Zenis restantes: {zenis_jogador - custo_total:,}.", aeternal_id))

    print(mensagem)

    conexao.commit()

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}", file=sys.stderr)
    sys.exit(1)
except Exception as erro:
    print(f"Erro: {erro}", file=sys.stderr)
    sys.exit(1)
finally:
    if cursor:
        cursor.close()
    if conexao and conexao.is_connected():
        conexao.close()
