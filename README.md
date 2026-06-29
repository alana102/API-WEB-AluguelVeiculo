# API-WEB-AluguelVeiculo
Trabalho 3 da disciplina de Desenvolvimento de Software para Persistência

## Diagrama de Classes

```mermaid
classDiagram
    class Ofertador {
        +str id
        +str nome
        +str CNPJ
        +str endereco
        +str status
    }
    class Cliente {
        +str id
        +str nome
        +str CPF
        +str telefone
        +str status
    }
    class Veiculo {
        +str id
        +Link~Ofertador~ ofertador
        +list~Link~Comodidade~~ comodidades
        +str placa
        +str modelo
        +str tipo
        +str status
    }
    class Comodidade {
        +str id
        +str nome
        +str descricao
    }
    class Aluguel {
        +str id
        +Link~Cliente~ cliente
        +Link~Veiculo~ veiculo
        +datetime data_inicio
        +datetime data_fim
        +str status
        +Pagamento pagamento
    }
    class Pagamento {
        <<Embedded>>
        +float valor_total
        +str metodo
        +datetime data_pagamento
    }
    class Documento {
        +str id
        +Link~Veiculo~ veiculo
        +str original_filename
        +str content_type
        +str extension
        +int size_bytes
        +datetime created_at
    }
    Ofertador <-- Veiculo : 1:N - Referencia (Link)
    Veiculo "*" <--> "*" Comodidade : N:N - Referencia (Link)
    Veiculo <-- Aluguel : N:1 - Referencia (Link)
    Cliente <-- Aluguel : N:1 - Referencia (Link)
    Veiculo <-- Documento : N:1 - Referencia (Link)
    Aluguel *-- Pagamento : Contém (Embedded)
```

## Como executar

### Com Docker (recomendado)
```bash
cp .env.exemplo .env
# preencha as credenciais no .env
docker compose up
```

### Localmente
```bash
cp .env.exemplo .env
# preencha as credenciais no .env
uv sync
uv run uvicorn app.main:app --reload
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

## Coleções

| Coleção | Descrição |
|---|---|
| `cliente` | Pessoas físicas que realizam aluguéis |
| `ofertador` | Empresas/pessoas que disponibilizam veículos |
| `veiculos` | Veículos disponíveis para aluguel |
| `comodidades` | Acessórios/equipamentos dos veículos (N:N com Veiculo) |
| `alugueis` | Registro de aluguéis com pagamento embutido |
| `documentos` | Arquivos associados a veículos, armazenados no MinIO |