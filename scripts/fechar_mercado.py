import sys
import mysql.connector
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

numero = sys.argv[1]

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="omniverse",
    ssl_disabled=True  # Desativa o SSL
)
cursor = conexao.cursor(dictionary=True)

try:
    # Verificar se o jogador é administrador
    cursor.execute("SELECT administrador FROM jogadores WHERE numero_whatsapp = %s", (numero,))
    jogador = cursor.fetchone()

    if not jogador:
        print("❌ Jogador não encontrado.")
        sys.exit()

    if not jogador['administrador']:
        print("❌ Você não tem permissão para abrir/fechar o mercado.")
        sys.exit()

    # Verificar o status atual do mercado
    cursor.execute("SELECT aberto_fechado FROM mercado WHERE id = 1")
    mercado = cursor.fetchone()

    if mercado['aberto_fechado'] == 0:
        print("❌ O mercado já está fechado.")
    else:
        # Fechar o mercado
        cursor.execute("UPDATE mercado SET aberto_fechado = 0 WHERE id = 1")
        conexao.commit()
        print("✅ Mercado fechado com sucesso!")

except mysql.connector.Error as erro:
    print(f"Erro no banco de dados: {erro}")
except Exception as erro:
    print(f"Erro: {erro}")

finally:
    cursor.close()
    conexao.close()