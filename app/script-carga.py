import asyncio
import io
from faker import Faker
import random
from motor.motor_asyncio import AsyncIOMotorClient

from app.modelos.aluguel import Aluguel, Pagamento
from app.modelos.cliente import Cliente
from app.modelos.documento import DocumentoModel
from app.modelos.ofertador import Ofertador
from app.modelos.veiculo import Veiculo
from app.modelos.comodidade import Comodidade

from datetime import timedelta, timezone
from beanie import init_beanie

from app.config.settings import settings
from app.config.minio_client import minio_client

fake = Faker("pt-br")

async def inicializar_banco():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    client.__dict__["append_metadata"] = lambda *args, **kwargs: None
    url_limpa = settings.MONGODB_URL.rstrip("/")
    db_name = url_limpa.split("/")[-1].split("?")[0]
    if not db_name or "." in db_name:
        db_name = "aluguel_veiculos"
        
    db = client[db_name]
    
    await init_beanie(
        database=db, 
        document_models=[Cliente, Veiculo, Ofertador, Aluguel, DocumentoModel, Comodidade]
    )
    print(f" Conectado ao banco: {db_name}")

async def gerar_clientes(qtd=100):
    clientes = []
    for _ in range(qtd):
        cliente = Cliente(
            nome=fake.name(),
            CPF=fake.cpf(),
            telefone=fake.phone_number(),
            status=random.choice(["Ativo", "Ativo", "Ativo", "Inativo"]) 
        )
        clientes.append(cliente.insert())
    
    resultados = await asyncio.gather(*clientes)
    print(f" {len(resultados)} Clientes gerados!")
    return resultados

async def gerar_ofertadores(qtd=100):
    ofertadores = []
    for _ in range(qtd):
        ofertador = Ofertador(
            nome=fake.company(),
            CNPJ=fake.cnpj(),
            endereco=fake.address(),
            status=random.choice(["Ativo", "Ativo", "Ativo", "Inativo"]) 
        )
        ofertadores.append(ofertador.insert())
    resultados = await asyncio.gather(*ofertadores)
    print(f" {len(resultados)} Ofertadores gerados!")
    return resultados

async def gerar_comodidades_base():
    nomes_comodidades = [
        "Ar Condicionado", "Direção Hidráulica", "Câmbio Automático", 
        "Vidros Elétricos", "Central Multimídia", "Sensor de Ré", 
        "Câmera de Ré", "Bancos de Couro", "Freios ABS", "Airbag Duplo"
    ]
    
    comodidades_salvas = []
    for nome in nomes_comodidades:
        existente = await Comodidade.find_one(Comodidade.nome == nome)
        if not existente:
            comodidade = Comodidade(nome=nome, descricao=f"Veículo equipado com {nome.lower()}.")
            await comodidade.insert()
            comodidades_salvas.append(comodidade)
        else:
            comodidades_salvas.append(existente)
            
    print(f" {len(comodidades_salvas)} Comodidades base prontas no banco!")
    return comodidades_salvas

async def gerar_veiculos_e_documentos(ofertadores,comodidades_disponiveis, qtd=100):
    veiculos_salvos = []
    documentos_tasks = []

    print(f" Gerando {qtd} veículos e seus respectivos documentos...")

    for _ in range(qtd):
        comodidades_veiculo = random.sample(comodidades_disponiveis, k=random.randint(1, 4))

        veiculo = Veiculo(
            placa=fake.bothify(text="???-#?##").upper(),
            tipo=random.choice(["Carro", "Moto"]),
            modelo=fake.word().capitalize(),
            status=random.choice(["Disponível", "Disponível", "Manutenção"]),
            ofertador=random.choice(ofertadores),
            comodidades=comodidades_veiculo
        )

        await veiculo.insert()
        veiculos_salvos.append(veiculo)


        doc_meta = DocumentoModel(
            original_filename="documento_veiculo.pdf",
            content_type="application/pdf",
            extension="pdf",
            size_bytes=1024,
            veiculo=veiculo 
        )
        
        async def salvar_documento_completo(meta=doc_meta):
            await meta.insert()
            physical_filename = f"{str(meta.id)}.pdf"
            try:
                await minio_client.put_object(
                    bucket_name=settings.MINIO_BUCKET_NAME,
                    object_name=physical_filename,
                    data=io.BytesIO(b"Conteudo ficticio de PDF de teste"),
                    length=32,
                    content_type="application/pdf"
                )
            except Exception as e:
                print(f"Aviso MinIO: Não foi possível enviar arquivo para o bucket. {e}")

        documentos_tasks.append(salvar_documento_completo())

    await asyncio.gather(*documentos_tasks)
    
    print(f" {len(veiculos_salvos)} Veículos (e seus 100 documentos no MinIO) gerados com sucesso!")
    return veiculos_salvos


async def gerar_alugueis(clientes, veiculos, qtd=100):
    alugueis = []
    
    clientes_ativos = [c for c in clientes if c.status == "Ativo"]
    
    if not clientes_ativos or not veiculos:
        print("Pulando geração de aluguéis: sem clientes ativos ou veículos disponíveis.")
        return []

    for _ in range(qtd):
        data_inicio = fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc)
        data_fim = data_inicio + timedelta(days=random.randint(2, 7))
        status_aluguel = random.choice(["Em andamento", "Finalizado", "Finalizado"])
        
        veiculo_escolhido = random.choice(veiculos)
        
        pagamento = None
        if status_aluguel == "Finalizado":
            pagamento = Pagamento(
                valor_total=round(random.uniform(150.0, 1200.0), 2),
                metodo=random.choice(["Cartão de Crédito", "Pix", "Dinheiro"]),
                data_pagamento=data_fim
            )
            veiculo_escolhido.status = "Disponível"
        else:
            veiculo_escolhido.status = "Alugado"
            
        await veiculo_escolhido.save()

        aluguel = Aluguel(
            cliente=random.choice(clientes_ativos),
            veiculo=veiculo_escolhido,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status_aluguel,
            pagamento=pagamento
        )
        alugueis.append(aluguel.insert())
        
    resultados = await asyncio.gather(*alugueis)
    print(f" {len(resultados)} Registros de Aluguéis gerados com sucesso!")
    return resultados

async def main():
    print(" Iniciando a carga de dados assíncrona...")
    
    await inicializar_banco()
    
    clientes_task = gerar_clientes(qtd=100)
    ofertadores_task = gerar_ofertadores(qtd=100)
    comodidades_task = gerar_comodidades_base()
    
    clientes, ofertadores, comodidades = await asyncio.gather(
        clientes_task, ofertadores_task, comodidades_task
    )

    veiculos = await gerar_veiculos_e_documentos(ofertadores, comodidades, qtd=100)
    
    await gerar_alugueis(clientes, veiculos, qtd=100)
    
    print("\n Carga finalizada perfeitamente! Banco pronto para uso.")

if __name__ == "__main__":
    asyncio.run(main())

