const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const { spawn } = require('child_process');

// Inicializa o cliente WhatsApp
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox'] // Desativa o sandbox do Chromium
    }
});

// Gera o QR Code para login
client.on('qr', async qr => {
    console.log("Gerando QR Code...");
    try {
        await qrcode.toFile('qr.png', qr);
        console.log("QR Code gerado como qr.png");
    } catch (error) {
        console.error("Erro ao gerar QR Code:", error);
    }
});

// Confirma quando o bot estiver pronto
client.on('ready', () => {
    console.log('Bot do WhatsApp está pronto!');
});

// Responde automaticamente a mensagens
client.on('message', async message => {
    const msg = message.body.toLowerCase().trim();
    const numero = message.from.replace(/@c\.us$/, ''); // Remove domínio do WhatsApp

    if (msg === 'placar') {
        const child = spawn('python3', ['scripts/status.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao buscar status.");
            }
        });
    } else if (msg.startsWith('upgrade')) {
        const partes = msg.split(' ');
        if (partes.length < 2) {
            message.reply(
                "✨ UPGRADE DE TÉCNICA! ✨\n\n" +
                "🔧 Quer melhorar uma técnica que já possui? Utilize o seguinte comando:\n\n" +
                "📌 *UPGRADE - [Nome da Técnica] - [Quantia de Upgrades]*\n\n" +
                "⚡ Se a quantidade de upgrades não for especificada, será aplicado apenas um upgrade por padrão!\n\n" +
                "🔔 *INFORMAÇÃO IMPORTANTE!*\n" +
                "    • ✨ Cada upgrade *dobra* o custo de *Saikōki* 🔹 e *dobra* o poder da técnica 💥.\n" +
                "    • 🔍 Certifique-se de ter *Saikōki suficiente* para poder utilizar a habilidade após o aprimoramento!\n" +
                "    • 🏆 Em técnicas cujo upgrade não excede *25.000 de poder*, será utilizado um *Sino de Prata*, que custa *100 Moedas de Treino* 🎟️ por aprimoramento.\n" +
                "    • Certifique-se de ter *Moedas de Treino suficientes* antes de tentar o aprimoramento!\n\n" +
                "🚀 Continue evoluindo suas habilidades e se tornando mais forte! 💪🔥"
            );
            return;
        }

        // Obtém o nome da técnica e a quantidade de upgrades (se especificada)
        const quantidade = isNaN(partes[partes.length - 1]) ? 1 : parseInt(partes.pop(), 10);
        const tecnica = partes.slice(1).join(' '); // Junta o restante como nome da técnica

        const child = spawn('python3', ['scripts/upar_tecnicas.py', numero, tecnica, quantidade.toString()]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao upar técnica.");
            }
        });
    } else if (msg === 'aprimorar') {
        message.reply("⚡ *Aprimoramento de Status* ⚡\n\nPara aprimorar seus atributos, siga um dos padrões abaixo e me envie:\n\t•\t*Vida:*\n\tAPRIMORAR - Vida - [Quantia] - [Item]\n\t•\t*Saikōki:*\n\tAPRIMORAR - Saikoki - [Quantia] - [Item]\n\t•\t*Força:*\n\tAPRIMORAR - Força - [Quantia] - [Item]\n\n *🔹NOTA:* O item de Vida e Saikōki deve ser substituído pelo *Rank da Moeda de Evolução* que você pretende utilizar. Ou seja, se for uma moeda de Rank F, você deve colocar “F”. Já o item da Força deve ser substituído pela letra que representa o upgrade desejado em sua força.\n\n *🔹Lembre-se de conferir o valor que cada upgrade concede ao seu status. Em casos de erros, o upgrade não ocorrerá.*\n\n*Se precisar de mais informações, estou aqui para ajudar! 💪.*");
        return;
    } else if (msg.startsWith('aprimorar ')) {
        const partes = msg.split(' ');
        if (partes.length < 3) {
            message.reply("⚡ *Aprimoramento de Status* ⚡\n\nPara aprimorar seus atributos, siga um dos padrões abaixo e me envie:\n\t•\t*Vida:*\n\tAPRIMORAR - Vida - [Quantia] - [Item]\n\t•\t*Saikōki:*\n\tAPRIMORAR - Saikoki - [Quantia] - [Item]\n\t•\t*Força:*\n\tAPRIMORAR - Força - [Quantia] - [Item]\n\n *🔹NOTA:* O item de Vida e Saikōki deve ser substituído pelo *Rank da Moeda de Evolução* que você pretende utilizar. Ou seja, se for uma moeda de Rank F, você deve colocar “F”. Já o item da Força deve ser substituído pela letra que representa o upgrade desejado em sua força.\n\n *🔹Lembre-se de conferir o valor que cada upgrade concede ao seu status. Em casos de erros, o upgrade não ocorrerá.*\n\n*Se precisar de mais informações, estou aqui para ajudar! 💪.*");
            return;
        }
        const status = partes[1];
        const quantidade = partes[2];
        const tipoMoeda = partes[3] || null; // Adicionado tipoMoeda

        if (status === "forca" && !tipoMoeda) {
            message.reply("Para aprimorar a força, você precisa especificar o item de força (por exemplo, K).");
            return;
        }

        const child = spawn('python3', ['scripts/upar_status.py', numero, status, quantidade, tipoMoeda]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao upar status.❌\n\n⚡ *Aprimoramento de Status* ⚡\n\nPara aprimorar seus atributos, siga um dos padrões abaixo e me envie:\n\t•\t*Vida:*\n\tAPRIMORAR - Vida - [Quantia] - [Item]\n\t•\t*Saikōki:*\n\tAPRIMORAR - Saikoki - [Quantia] - [Item]\n\t•\t*Força:*\n\tAPRIMORAR - Força - [Quantia] - [Item]\n\n *🔹NOTA:* O item de Vida e Saikōki deve ser substituído pelo *Rank da Moeda de Evolução* que você pretende utilizar. Ou seja, se for uma moeda de Rank F, você deve colocar “F”. Já o item da Força deve ser substituído pela letra que representa o upgrade desejado em sua força.\n\n *🔹Lembre-se de conferir o valor que cada upgrade concede ao seu status. Em casos de erros, o upgrade não ocorrerá.*\n\n*Se precisar de mais informações, estou aqui para ajudar! 💪.*");
            }
        });
    } else if (msg.startsWith('mercado')) {
        const partes = msg.split(' ');
        let categoria = null;
        if (partes.length > 1) {
            categoria = partes.slice(1).join(' '); // Junta o restante como nome da categoria
        }

        const args = ['scripts/listar_tecnicas.py', numero];
        if (categoria) {
            args.push(categoria); // Adiciona o nome da categoria como argumento
        }

        const child = spawn('python3', args);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao listar técnicas.");
            }
        });
    }else if (msg.startsWith('comprar')) {
        const partes = msg.split(' ');
        if (partes.length < 2) {
            message.reply(
                "✨ COMPRA DE TÉCNICA! ✨\n\n" +
                "🔧 Quer adquirir uma nova técnica? Utilize o seguinte comando:\n\n" +
                "📌 *COMPRAR - [Nome da Técnica]*\n\n" +
                "🔔 *INFORMAÇÃO IMPORTANTE!*\n" +
                "    • ✨ Ao adquirir uma nova técnica o valor da mesma será descontado dos seus Zenis 💥.\n" +
                "    • 🔍 Certifique-se de ter *Zenis suficientes* para adquirir uma nova técnica!\n" +
                "    • 🏆 Em técnicas cujo a classe do jogador for inferior não poderão ser obtidas!\n" +
                "    • Certifique-se de cumprir todos os *requisitos* para adquirir uma nova habilidade!\n\n" +
                "🚀 Continue adquirindo novas habilidades e se tornando mais forte! 💪🔥"
            );
            return;
        }

        const tecnica = partes.slice(1).join(' '); // Junta o restante como nome da técnica

        const child = spawn('python3', ['scripts/comprar_tecnica.py', numero, tecnica]);

        const output = []; // Array para armazenar as mensagens do script Python

        child.stdout.on('data', (data) => {
            output.push(data.toString()); // Adiciona a mensagem ao array
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao comprar técnica.");
            } else {
                // Envia as mensagens separadamente
                if (output.length > 0) {
                    message.reply(output[0]); // Envia o card da técnica
                    if (output.length > 1) {
                        message.reply(output[1]); // Envia a mensagem de confirmação
                    }
                }
            }
        });
    }else if (msg.startsWith('fisico') || msg.startsWith('físico')) {
        const partes = msg.split(' ');
        if (partes.length < 2) {
            message.reply(
                "🥋 *Taijutsu Atualizado!* 🥋\n\n" +
                "*💪 Seu poder físico aumentou?*\n\n" +
                "📌 Para receber a nova versão da sua técnica, utilize o comando:\n" +
                "*Físico - [Nome da Técnica]*\n\n" +
                "⚡ Lembre-se: técnicas físicas podem ser aprimoradas conforme sua força aumenta!\n\n" +
                "*🔥 Continue treinando e dominando seu Taijutsu! 🚀*"
            );
            return;
        }

        const tecnica = partes.slice(1).join(' '); // Junta o restante como nome da técnica

        const child = spawn('python3', ['scripts/taijutsu.py', numero, tecnica]);

        const output = []; // Array para armazenar as mensagens do script Python

        child.stdout.on('data', (data) => {
            output.push(data.toString()); // Adiciona a mensagem ao array
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao exibir Taijutsu.");
            } else {
                // Envia as mensagens separadamente
                if (output.length > 0) {
                    message.reply(output[0]); // Envia o card da técnica
                    if (output.length > 1) {
                        message.reply(output[1]); // Envia a mensagem de confirmação
                    }
                }
            }
        });
    }else if (msg === 'perfil') {
        const child = spawn('python3', ['scripts/perfil.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao exibir perfil.");
            }
        });
    }else if (msg === '!log') {
        const child = spawn('python3', ['scripts/log.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao exibir log.");
            }
        });
    }else if (msg.startsWith('aeternal')) {
    const partes = msg.split(' ');
    
    if (partes.length === 1) {
        // Listar os Aeternals do jogador
        const child = spawn('python3', ['scripts/listar_aeternals.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao verificar Aeternals.");
            }
        });
    } else if (partes.length < 3) {
        // Instruções de uso
        message.reply(
            "🛠 *Quer aprimorar um Aeternal?* Utilize o seguinte comando:\n" +
            "📌 *Aeternal - [Nome] - [Quantia de UP]*\n" +
            "📌 *Ou use:* Aeternal - [Nome] - [Quantia] - Super\n\n" +
            "🔹 *Exemplo:*\n" +
            "📌 Aeternal - Aquatyl - 2\n" +
            "📌 Aeternal - Shin Goku - 5 - Super\n\n" +
            "📖 *Explicação:*\n" +
            "\t• Cada upgrade aumenta a Vida do Aeternal!\n" +
            "\t• 🍬 *Normal Candy:* +100 Vida / 500 Zenis\n" +
            "\t• 🍬 *Super Candy:* +1000 Vida / 4.000 Zenis\n" +
            "\t• 🌟 *A evolução ocorre ao atingir o nível máximo da fase atual.*\n"
        );
        return;
    } else {
        const tipo_doce = (partes.length >= 4 && partes[3].toLowerCase().includes("super")) ? "super" : "normal";
        const quantidade = parseInt(partes[2].trim(), 10);
        const aeternal = partes[1].trim();

        const args = ['scripts/upar_aeternal.py', numero, aeternal, quantidade.toString(), tipo_doce];
        const child = spawn('python3', args);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌ Erro ao aprimorar Aeternal.");
            }
        });
    }
    }else if (msg.startsWith('!abrir')) {
        const child = spawn('python3', ['scripts/abrir_mercado.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao abrir mercado.");
            }
        });
    }else if (msg.startsWith('!fechar')) {
        const child = spawn('python3', ['scripts/fechar_mercado.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao fechar mercado.");
            }
        });
    }else if (msg.startsWith('!missao') || msg.startsWith('!missão')) {
        const partes = msg.split(' ');
        if (partes.length < 3) {
            message.reply("Uso: !missao [nickname] [rank] [quantidade (opcional)]");
            return;
        }

        let rankIndex = -1;
        for (let i = 1; i < partes.length; i++) {
            if (partes[i].length === 1 && partes[i].match(/[A-Za-z]/)) { // Encontra o índice do rank
                rankIndex = i;
                break;
            }
        }

        if (rankIndex === -1) {
            message.reply("Formato inválido. Certifique-se de incluir o rank.");
            return;
        }

        const nickname = partes.slice(1, rankIndex).join(' '); // Extrai o nickname composto
        const rank = partes[rankIndex].toUpperCase(); // Garante que o rank esteja em maiúsculo
        const quantidade = partes[rankIndex + 1] ? parseInt(partes[rankIndex + 1], 10) : 1; // Quantidade padrão é 1

        const child = spawn('python3', ['scripts/marcar_missao.py', numero, nickname, rank, quantidade.toString()]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao marcar missão concluída.");
            }
        });
    }else if (msg.startsWith('!vd')) {
        const partes = msg.split(' ');
        if (partes.length < 4) {
            message.reply("Uso: !vd [nickname] [V/D] [quantidade]");
            return;
        }

        let vdIndex = -1;
        for (let i = 1; i < partes.length; i++) {
            if (partes[i].length === 1 && (partes[i].toUpperCase() === 'V' || partes[i].toUpperCase() === 'D')) { // Encontra o índice de V/D
                vdIndex = i;
                break;
            }
        }

        if (vdIndex === -1) {
            message.reply("Formato inválido. Certifique-se de incluir V ou D.");
            return;
        }

        const nickname = partes.slice(1, vdIndex).join(' '); // Extrai o nickname composto
        const vd = partes[vdIndex].toUpperCase(); // Garante que V ou D esteja em maiúsculo
        const quantidade = parseInt(partes[vdIndex + 1], 10);

        const child = spawn('python3', ['scripts/adicionar_vd.py', numero, nickname, vd, quantidade.toString()]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao adicionar vitórias/derrotas.");
            }
        });
    }else if (msg === 'ajuda') {
        message.reply(
            "🌟 *Lista de Comandos Disponíveis* 🌟\n\n" +
        "👤 *Perfil:* Veja informações detalhadas do seu personagem.\n" +
        "   📌 Comando: *perfil*\n\n" +

        "💠 *Placar:* Veja seu status atual.\n" +
        "   📌 Comando: *placar*\n\n" +

        "⚡ *Upgrade de Técnicas:* Aprimore suas técnicas existentes.\n" +
        "   📌 Comando: *upgrade - [Nome da Técnica] - [Quantidade]*\n" +
        "   💡 Se a quantidade não for especificada, será aplicado um upgrade.\n\n" +

        "🏋️ *Aprimoramento de Status:* Melhore Vida, Saikōki ou Força.\n" +
        "   📌 Comando: *aprimorar - [Atributo] - [Quantia] - [Item]*\n" +
        "   🔹 Exemplo: *aprimorar - vida - 1000 - E*\n\n" +

        "🛒 *Mercado:* Veja as técnicas disponíveis para compra.\n" +
        "   📌 Comando: *mercado* ou *mercado - [Categoria]*\n\n" +

        "🛍️ *Comprar Técnicas:* Adquira novas habilidades.\n" +
        "   📌 Comando: *comprar - [Nome da Técnica]*\n\n" +

        "📜 *Solicitar Técnicas:* Recupere o card de uma técnica que já possui.\n" +
        "   📌 Comando: *solicitar - [Nome da Técnica]*\n\n" +

        "🥋 *Atualizar Técnicas Físicas:* Se sua força aumentou, recupere a técnica com os novos valores.\n" +
        "   📌 Comando: *físico - [Nome da Técnica]*\n\n" +

        "🔮 *Aeternals:* Gerencie seus Aeternals.\n" +
        "   📌 Comando: *aeternal* → Lista os seus Aeternals.\n" +
        "   📌 Comando: *aeternal - [Nome] - [Quantidade de Upgrades]* → Aumenta a resistência do Aeternal.\n\n" +

        "🚀 *Dica:* Certifique-se de ter os recursos necessários antes de tentar um upgrade ou compra!\n\n" +

        "🔹 *Continue treinando e evoluindo!* 💪🔥"
        );
    }else if (msg.startsWith('!add')) {
        const partes = msg.split(' ');
        if (partes.length < 4) { // Garantir que haja pelo menos !tec + nickname(2) + técnica(1)
            message.reply("Uso: !add [nickname] [nome da técnica] [opcional: quantidade de upgrades]");
            return;
        }
    
        const nickname = partes.slice(1, 3).join(' '); // Pegando as duas primeiras palavras como nickname
        
        let tecnica, upgrades;
        if (!isNaN(partes[partes.length - 1])) {
            // Se o último argumento for um número, é a quantidade de upgrades
            upgrades = partes.pop(); // Remove o último elemento da lista e usa como upgrades
            tecnica = partes.slice(3).join(' '); // O restante da mensagem é a técnica
        } else {
            // Se não houver número, assume que upgrades = 0
            upgrades = 0;
            tecnica = partes.slice(3).join(' '); // O restante da mensagem é a técnica
        }
    
        const child = spawn('python3', ['scripts/associar_tecnica.py', numero, nickname, tecnica, upgrades]);
    
        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao associar técnica.");
            }
        });
    }else if (msg.startsWith('!tec')) {
        const partes = msg.split(' ');
    
        if (partes.length < 2) { // Garante que tenha pelo menos "!tec" + nickname
            message.reply("Uso: !tec [nickname]");
            return;
        }
    
        const nickname = partes.slice(1).join(' '); // Captura todo o restante como nickname
    
        const child = spawn('python3', ['scripts/listar_tecnicas_alheias.py', numero, nickname]);
    
        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao listar técnicas.");
            }
        });
    }else if (msg.startsWith('solicitar')) {
        const partes = msg.split(' ');
        if (partes.length < 2) {
            message.reply("Uso: solicitar [nome da técnica]");
            return;
        }
    
        const nomeTecnica = partes.slice(1).join(' '); // Junta o restante como nome da técnica
    
        const child = spawn('python3', ['scripts/solicitar_card.py', numero, nomeTecnica]);
    
        const output = []; // Array para armazenar as mensagens do script Python
    
        child.stdout.on('data', (data) => {
            output.push(data.toString()); // Adiciona a mensagem ao array
        });
    
        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });
    
        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao solicitar card da técnica.");
            } else {
                // Envia as mensagens separadamente
                if (output.length > 0) {
                    message.reply(output[0]); // Envia o card da técnica
                }
            }
        });
    }else if (msg.startsWith('!cupom')) {
        const partes = msg.split(' ');
        if (partes.length < 3) {
            message.reply("Uso: !cupom [nickname] [rank] [quantidade (opcional)]");
            return;
        }

        let rankIndex = -1;
        for (let i = 1; i < partes.length; i++) {
            if (partes[i].length === 1 && partes[i].match(/[A-Za-z]/)) { // Encontra o índice do rank
                rankIndex = i;
                break;
            }
        }

        if (rankIndex === -1) {
            message.reply("Formato inválido. Certifique-se de incluir o rank.");
            return;
        }

        const nickname = partes.slice(1, rankIndex).join(' '); // Extrai o nickname composto
        const rank = partes[rankIndex].toUpperCase(); // Garante que o rank esteja em maiúsculo
        const quantidade = partes[rankIndex + 1] ? parseInt(partes[rankIndex + 1], 10) : 1; // Quantidade padrão é 1

        const child = spawn('python3', ['scripts/cupom.py', numero, nickname, rank, quantidade.toString()]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao marcar missão concluída.");
            }
        });
    }else if (msg.startsWith('!req')) {
        const partes = msg.split(' ');
        if (partes.length < 3) { // Pelo menos !req + nickname(2) + nome do requisito(1)
            message.reply("Uso: !req [nickname] [nome do requisito]");
            return;
        }
    
        const nickname = partes.slice(1, 3).join(' '); // Pegando as duas primeiras palavras como nickname
        const requisito = partes.slice(3).join(' '); // Todo o resto é o nome do requisito
    
        const child = spawn('python3', ['scripts/associar_requisito.py', numero, nickname, requisito]);
    
        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("Erro ao associar requisito.");
            }
        });
    }else if (msg.startsWith('!inicial')) {
        const partes = msg.split(' ');
        if (partes.length < 2) {
            message.reply("Uso: !inicial [nome do Aeternal]\nEx: !inicial Aquatyl");
            return;
        }
    
        const nomeAeternal = partes.slice(1).join(' '); // Suporta nomes compostos (se houver futuramente)
    
        const child = spawn('python3', ['scripts/escolher_aeternal.py', numero, nomeAeternal]);
    
        let resposta = "";
    
        child.stdout.on('data', (data) => {
            resposta += data.toString();
        });
    
        child.stderr.on('data', (data) => {
            message.reply(data.toString());
        });
    
        child.on('close', (code) => {
            // Se a resposta contiver um marcador de imagem, envia imagem
            const match = resposta.match(/\[imagem\](.*\.png)/);
            if (match) {
                const caminhoImagem = match[1].trim();
                const legenda = resposta.replace(match[0], "").trim();
    
                message.reply(new MessageMedia('image/png', fs.readFileSync(caminhoImagem, { encoding: 'base64' }), `${nomeAeternal}.png`), { caption: legenda });
            } else {
                message.reply(resposta.trim());
            }
        });
    }else if (msg.startsWith('!aet')) {
    const partes = msg.split(' ');
    if (partes.length < 3) { // Pelo menos !addaet + nickname(2) + nome do aeternal(1)
        message.reply("Uso: !aet [nickname] [nome do Aeternal]");
        return;
    }

    const nickname = partes.slice(1, 3).join(' '); // As duas primeiras palavras como nickname
    const nomeAeternal = partes.slice(3).join(' '); // Todo o restante é o nome do Aeternal

    const child = spawn('python3', ['scripts/adicionar_aeternal.py', numero, nickname, nomeAeternal]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("Erro ao adicionar Aeternal ao jogador.");
        }
    });
}else if (msg.startsWith('!perfil')) {
    const partes = msg.split(' ');
    
    if (partes.length < 2) {
        message.reply("📌 *Use o comando corretamente:*\n!perfil Last Nome");
        return;
    }

    const nomeCompleto = partes.slice(1).join(' '); // Junta tudo após "!perfil"

    const child = spawn('python3', ['scripts/perfil_outro_jogador.py', nomeCompleto]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao exibir perfil do jogador informado.");
        }
    });
}else if (msg.startsWith('!vreq')) {
    const partes = msg.split(' ');

    if (partes.length < 2) {
        message.reply("📌 *Use o comando corretamente:*\n!vreq Last Nome");
        return;
    }

    const nomeCompleto = partes.slice(1).join(' '); // Junta tudo após "!requisitos"

    const child = spawn('python3', ['scripts/listar_requisitos_jogador.py', nomeCompleto]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao buscar requisitos do jogador informado.");
        }
    });
}else if (msg.startsWith('!subir')) {
    const partes = msg.split(' ');

    if (partes.length < 3) {
        message.reply("📌 *Uso correto do comando:*\n!Subir Last Nome Classe\n\n🔹 *Exemplo:* !Subir Last Lonely D");
        return;
    }

    const nomeCompleto = partes.slice(1, -1).join(' ');
    const novaClasse = partes[partes.length - 1].toUpperCase(); // Ex: D, C, B...

    const child = spawn('python3', ['scripts/verificar_subida_classe.py', nomeCompleto, novaClasse]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao verificar subida de classe.");
        }
    });
}else if (msg.startsWith('!zenis')) {
    const partes = msg.split(' ');
    if (partes.length < 3) { // Pelo menos !zenis + nickname(2) + quantidade(1)
        message.reply("Uso: !zenis [nickname] quantidade");
        return;
    }

    const nickname = partes.slice(1, 3).join(' '); // As duas primeiras palavras como nickname
    const quantidade = partes[3]; // A terceira palavra como quantidade

    const child = spawn('python3', ['scripts/adicionar_zenis.py', numero, nickname, quantidade]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("Erro ao adicionar Zenis ao jogador.");
        }
    });
}else if (msg.startsWith('!tc')) {
    const partes = msg.split(' ');
    if (partes.length < 3) { // Pelo menos !tc + nickname(2) + nome do tc(1)
        message.reply("Uso: !tc [nickname] quantidade");
        return;
    }

    const nickname = partes.slice(1, 3).join(' '); // As duas primeiras palavras como nickname
    const quantidade = partes[3]; // A terceira palavra como quantidade

    const child = spawn('python3', ['scripts/adicionar_tc.py', numero, nickname, quantidade]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("Erro ao adicionar TC ao jogador.");
        }
    });
}else if (msg === '!historico') {
        const child = spawn('python3', ['scripts/historico.py', numero]);

        child.stdout.on('data', (data) => {
            message.reply(data.toString());
        });

        child.stderr.on('data', (data) => {
            message.reply(data.toString()); // Envia a saída de erro para o WhatsApp
        });

        child.on('close', (code) => {
            if (code !== 0) {
                message.reply("❌Erro ao exibir log.");
            }
        });
    }else if (msg.startsWith('!areq')) {
    const partes = msg.split(' ');

    if (partes.length < 2) {
        message.reply("📌 *Use o comando corretamente:*\n!areq Nome do requisito");
        return;
    }

    const nomeCompleto = partes.slice(1).join(' '); // Junta tudo após "!areq"
    const child = spawn('python3', ['scripts/listar_jogador_por_requisito.py', nomeCompleto]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao buscar requisitos do jogador informado.");
        }
    });
}else if (msg.startsWith('!atitulo')) {
    const partes = msg.split(' ');

    if (partes.length < 3) {
        message.reply("📌 *Uso correto do comando:*\n!titulo NomeDoJogador Nome do título\n\n🔹 *Exemplo:* !titulo Last Lonely Guerreiro do Caos");
        return;
    }

    const nomeJogador = partes.slice(1, 3).join(' '); // Junta as duas primeiras palavras como nome do jogador
    const titulo = partes.slice(3).join(' '); // Junta o restante como título

    const child = spawn('python3', ['scripts/associar_titulo_jogador.py', numero, nomeJogador, titulo]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao associar título ao jogador.");
        }
    });
}else if (msg.startsWith('!ltitulos')) {
    const partes = msg.split(' ');

    if (partes.length < 2) {
        message.reply("📌 *Uso correto do comando:*\n!ltitulos NomeDoJogador\n\n🔹 *Exemplo:* !ltitulos Last Lonely");
        return;
    }

    const nomeJogador = partes.slice(1, 3).join(' ');

    const child = spawn('python3', ['scripts/listar_titulos_jogador.py', nomeJogador]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao listar títulos do jogador.");
        }
    });
}else if (msg === '!comandos_adm') {
    const comandos = `
*🔐 COMANDOS DE ADMINISTRADOR 🔐*

📂 *!log* — Exibe o histórico de transações do jogador.
🚪 *!abrir* — Abre o servidor para entrada de novos jogadores.
🔒 *!fechar* — Fecha o servidor para novos registros.
📝 *!missão* — Marca a missão como concluída para o jogador.
⚔️ *!vd* — Atualiza vitórias e derrotas de um jogador.
➕ *!add* — Adiciona recursos manualmente (zenis, tc etc).
🎟️ *!cupom* — Gera cupons de bônus para jogadores.
📜 *!req* — Associa um requisito a um jogador.
🌪️ *!aet* — Adiciona um Aeternal ao jogador.
💰 *!zenis* — Adiciona Zenis ao jogador.
🏋️ *!tc* — Adiciona Training Coins ao jogador.
📖 *!historico* — Mostra o histórico de compras do jogador.
🔎 *!areq* — Lista jogadores que possuem determinado requisito.
🏅 *!titulo* — Registra um novo título para um jogador.
`;

    message.reply(comandos);
}else if (msg.startsWith('!treq')) {
    const partes = msg.split(' ');

    if (partes.length < 3) {
        message.reply("📌 *Uso correto do comando:*\n!treq NomeDoJogador Nome do Requisito\n\n🔹 *Exemplo:* !treq Last Lonely Manipulação de Água");
        return;
    }

    // Captura nome do jogador (2 primeiras palavras)
    const nomeJogador = partes.slice(1, 3).join(' '); // Junta as duas primeiras palavras como nome do jogador

    // Captura o restante como nome do requisito
    const requerimento = partes.slice(3).join(' ');

    const child = spawn('python3', ['scripts/tecnicas_por_requerimento.py', nomeJogador, requerimento]);

    child.stdout.on('data', (data) => {
        message.reply(data.toString());
    });

    child.stderr.on('data', (data) => {
        message.reply(data.toString());
    });

    child.on('close', (code) => {
        if (code !== 0) {
            message.reply("❌ Erro ao verificar técnicas.");
        }
    });
}


        

});

client.initialize();