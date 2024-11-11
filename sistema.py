import json

# Estruturas de dados para o sistema
veiculos = []
motoristas = []
pedidos = []
localizacoes = {}  # Dicionário para rastreamento de localizações de veículos
motoristas_irregulares = set()  # Conjunto para motoristas em situação irregular

# Funções para o sistema de logística

def salvar_dados():
    dados = {
        "veiculos": veiculos,
        "motoristas": motoristas,
        "pedidos": pedidos,
        "localizacoes": localizacoes,
        "motoristas_irregulares": list(motoristas_irregulares)
    }
    with open("dados_logistica.json", "w") as f:
        json.dump(dados, f, indent=4)
    print("Dados salvos com sucesso.")

def carregar_dados():
    global veiculos, motoristas, pedidos, localizacoes, motoristas_irregulares
    try:
        with open("dados_logistica.json", "r") as f:
            dados = json.load(f)
            veiculos = dados.get("veiculos", [])
            motoristas = dados.get("motoristas", [])
            pedidos = dados.get("pedidos", [])
            localizacoes = dados.get("localizacoes", {})
            motoristas_irregulares = set(dados.get("motoristas_irregulares", []))
        print("Dados carregados com sucesso.")
    except FileNotFoundError:
        print("Nenhum arquivo de dados encontrado. Um novo será criado.")
    except json.JSONDecodeError:
        print("Erro: Arquivo de dados corrompido. Será necessário iniciar com dados novos.")

def cadastrar_veiculo():
    id_veiculo = input("ID do Veículo: ")
    if any(v["id"] == id_veiculo for v in veiculos):
        print("Erro: ID do veículo já existe.")
        return

    modelo = input("Modelo do Veículo: ")
    try:
        capacidade_carga = int(input("Capacidade de Carga (em kg): "))
    except ValueError:
        print("Erro: Capacidade de carga deve ser um número inteiro.")
        return

    categoria_habilitacao = input("Categoria de Habilitação Necessária (ex: B, C, D): ").upper()
    veiculo = {
        "id": id_veiculo,
        "modelo": modelo,
        "capacidade_carga": capacidade_carga,
        "categoria_habilitacao": categoria_habilitacao,
        "disponibilidade": "disponível"
    }
    veiculos.append(veiculo)
    salvar_dados()
    print("Veículo cadastrado com sucesso.")

def cadastrar_motorista():
    id_motorista = input("ID do Motorista: ")
    if any(m["id"] == id_motorista for m in motoristas):
        print("Erro: ID do motorista já existe.")
        return

    nome = input("Nome do Motorista: ")
    id_veiculo = input("ID do Veículo que o motorista dirige: ")
    tipo_habilitacao = input("Tipo de Habilitação (ex: B, C, D): ").upper().split(",")
    
    motorista = {
        "id": id_motorista,
        "nome": nome,
        "veiculo_id": id_veiculo,
        "tipo_habilitacao": tipo_habilitacao
    }
    motoristas.append(motorista)
    salvar_dados()
    print("Motorista cadastrado com sucesso.")

def registrar_pedido():
    id_pedido = input("ID do Pedido: ")
    if any(p["id"] == id_pedido for p in pedidos):
        print("Erro: ID do pedido já existe.")
        return

    try:
        peso = int(input("Peso do Pedido (em kg): "))
    except ValueError:
        print("Erro: O peso do pedido deve ser um número inteiro.")
        return

    endereco = input("Endereço de Entrega: ")
    pedido = {
        "id": id_pedido,
        "peso": peso,
        "endereco": endereco,
        "status": "pendente",
        "motorista_id": None,
        "veiculo_id": None
    }
    pedidos.append(pedido)
    salvar_dados()
    print("Pedido registrado com sucesso.")

def atribuir_entrega():
    id_pedido = input("ID do Pedido para atribuição: ")
    id_motorista = input("ID do Motorista para a entrega: ")

    pedido = next((p for p in pedidos if p["id"] == id_pedido), None)
    motorista = next((m for m in motoristas if m["id"] == id_motorista), None)
    veiculo = next((v for v in veiculos if v["id"] == motorista["veiculo_id"]), None) if motorista else None
    
    if not pedido or not motorista or not veiculo:
        print("Erro: Pedido, motorista ou veículo não encontrado.")
        return

    if pedido["peso"] > veiculo["capacidade_carga"]:
        print("Erro: O peso do pedido excede a capacidade do veículo.")
        return

    # Verificar se o motorista possui a habilitação necessária para o tipo de veículo
    if veiculo["categoria_habilitacao"] not in motorista["tipo_habilitacao"]:
        motoristas_irregulares.add(motorista["nome"])
        print("Aviso: Motorista não possui habilitação adequada para o veículo e foi marcado como irregular.")

    pedido["status"] = "em trânsito"
    pedido["motorista_id"] = id_motorista
    pedido["veiculo_id"] = veiculo["id"]
    veiculo["disponibilidade"] = "em uso"
    salvar_dados()
    print(f"Pedido {id_pedido} atribuído ao motorista {motorista['nome']} e veículo {veiculo['id']}.")

def atualizar_localizacao():
    id_veiculo = input("ID do Veículo para atualizar a localização: ")
    try:
        latitude = float(input("Latitude: "))
        longitude = float(input("Longitude: "))
    except ValueError:
        print("Erro: Coordenadas inválidas. Devem ser números.")
        return

    if id_veiculo not in [v["id"] for v in veiculos]:
        print("Erro: Veículo não encontrado.")
        return

    # Validação de coordenadas
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        print("Erro: Coordenadas inválidas. Tente novamente.")
        return

    localizacoes[id_veiculo] = (latitude, longitude)
    salvar_dados()
    print(f"Localização do veículo {id_veiculo} atualizada para ({latitude}, {longitude}).")

def relatorio_pedidos_em_transito():
    print("Relatório de pedidos em trânsito:")
    for pedido in pedidos:
        if pedido["status"] == "em trânsito":
            motorista = next((m for m in motoristas if m["id"] == pedido["motorista_id"]), None)
            print(f"Pedido {pedido['id']} - Endereço: {pedido['endereco']}, Motorista: {motorista['nome'] if motorista else 'Desconhecido'}")

def relatorio_motoristas_irregulares():
    print("Relatório de motoristas em situação irregular:")
    for motorista in motoristas_irregulares:
        print(f"Motorista: {motorista}")

def relatorio_pedidos_pendentes():
    print("Relatório de pedidos pendentes:")
    for pedido in pedidos:
        if pedido["status"] == "pendente":
            print(f"Pedido {pedido['id']} - Endereço: {pedido['endereco']}")

def menu():
    carregar_dados()
    while True:
        print("\nSistema de Gestão de Logística")
        print("1. Cadastrar Veículo")
        print("2. Cadastrar Motorista")
        print("3. Registrar Pedido")
        print("4. Atribuir Entrega")
        print("5. Atualizar Localização de Veículo")
        print("6. Relatório de Pedidos em Trânsito")
        print("7. Relatório de Motoristas Irregulares")
        print("8. Relatório de Pedidos Pendentes")
        print("9. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_veiculo()
        elif opcao == "2":
            cadastrar_motorista()
        elif opcao == "3":
            registrar_pedido()
        elif opcao == "4":
            atribuir_entrega()
        elif opcao == "5":
            atualizar_localizacao()
        elif opcao == "6":
            relatorio_pedidos_em_transito()
        elif opcao == "7":
            relatorio_motoristas_irregulares()
        elif opcao == "8":
            relatorio_pedidos_pendentes()
        elif opcao == "9":
            print("Saindo do sistema.")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Executa o menu principal
menu()
