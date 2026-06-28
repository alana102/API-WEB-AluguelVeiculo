# API-WEB-AluguelVeiculo
Trabalho 3 da disciplina de Desenvolvimento de Software para Persistência

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
        class Veiculo{
            +str id
            +Link~Ofertador~ ofertador
            +str placa
            +str modelo
            +str status
        }
        class Aluguel{
            +str id
            +Link~Cliente~ cliente
            +Link~Veiculo~ veiculo
            +datetime data_inicio
            +datetime data_fim
            +str status
            +Pagamento pagamento
        }
        class Pagamento{
            <<Embedded>>
            +float valor_total
            +str metodo
            +datetime data_pagamento
        }
        class Documento{
            +str id
            +Link~Veiculo~ veiculo
            +str original_filename
            +str content_type
            +str extension
            +int size_byte
            +datetime created_at
        }
        Ofertador <-- Veiculo : Referencia(Link)
        Veiculo <-- Aluguel : Referencia(Link)
        Cliente <-- Aluguel : Referencia (Link)
        Veiculo <-- Documento : Referencia (Link)
        Aluguel *-- Pagamento : Contém (Embed)
