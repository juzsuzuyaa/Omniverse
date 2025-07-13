import io
import sys
import mysql.connector

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True
)
cursor = conexao.cursor(dictionary=True)

# Buscar informações do jogador
cursor.execute("SELECT numero_registro, simbolo, nickname, vida, saikoki FROM jogadores WHERE numero_whatsapp = %s", (numero,))
jogador = cursor.fetchone()

if jogador:
    vida_base = jogador['vida']
    vida_final = vida_base
    vida_multiplicador = 1.0

    # Buscar passivas do jogador com placar = 1
    cursor.execute("""
        SELECT p.card, p.nome, p.aumento, p.quantidade
        FROM passivas p
        INNER JOIN jogadores_passivas jp ON p.id = jp.passivas_id
        WHERE jp.jogadores_id = %s AND p.placar = 1
    """, (jogador['numero_registro'],))
    passivas = cursor.fetchall()

    # Separar passivas que aumentam a vida
    passivas_vida = [p for p in passivas if p['aumento'] and p['quantidade']]

    # Processar Ascensões primeiro
    passivas_vida.sort(key=lambda p: (not p['nome'].startswith("Ascensão"), p['nome']))

    # Aplicar multiplicadores
    for p in passivas_vida:
        try:
            vida_multiplicador *= (1 + float(p['quantidade']))
        except:
            continue  # Ignora valores inválidos

    vida_final = int(vida_base * vida_multiplicador)

    vida_formatada = "{:,}".format(vida_final)
    saikoki_formatado = "{:,}".format(int(jogador['saikoki']))

    resposta = f"[{jogador['simbolo']}]{jogador['nickname']}\n➖Life: {vida_formatada}\n➖Saikōki: {saikoki_formatado}"

    # Reordenar passivas para mostrar as Ascensões primeiro
    passivas.sort(key=lambda p: (not p['nome'].startswith("Ascensão"), p['nome']))
    if passivas:
        resposta += "\n" + "\n".join(p['card'] for p in passivas)

else:
    resposta = f"❌ Jogador não encontrado (Número: {numero})."

print(resposta + "\n 《↭〰↭〰《VS》〰↭〰↭》")

cursor.close()
conexao.close()
