# BTime RPA Challenge

Desafio técnico para a vaga de Desenvolvedor RPA.

## Objetivo

Desenvolver dois scripts Python para automatizar a coleta de cotações de moedas utilizando fontes públicas distintas:

1. **Web Scraping:** coleta de cotações USD/BRL e EUR/BRL no Google Finance utilizando Requests e BeautifulSoup.
2. **API REST:** coleta das mesmas cotações por meio da AwesomeAPI.

Os dados são normalizados em um formato comum e exportados para arquivos CSV independentes.

## Tecnologias

- Python 3.12
- Poetry — gerenciamento de dependências
- Requests — requisições HTTP
- BeautifulSoup — extração de dados HTML
- Pytest — testes automatizados
- pytest-cov — cobertura de código

## Arquitetura

O projeto utiliza uma Arquitetura Hexagonal simplificada, separando regras de negócio das implementações de infraestrutura.

A organização está dividida em:

- **Domain:** entidades e contratos (ports).
- **Application:** casos de uso responsáveis pela orquestração.
- **Infrastructure:** adaptadores para API, scraping e exportação CSV.
- **Entrypoints:** scripts responsáveis pela inicialização de cada fluxo.

Essa separação permite substituir fontes de dados ou mecanismos de exportação sem alterar as regras centrais da aplicação.

## Instalação

### Pré-requisitos

- Python 3.12
- Poetry
- Git
- Conexão com a internet

Clone o repositório:

```bash
git clone https://github.com/PedroHAquino/btime-rpa-challenge.git
cd btime-rpa-challenge
```

Instale as dependências:

```bash
poetry install
```

## Execução

Execute os comandos a partir da raiz do projeto.

### Script 1 — Web Scraping

```bash
poetry run python -m btime_rpa.run_scraping
```

O script coleta as cotações no Google Finance e gera:

`data/scraping_exchange_rates.csv`

### Script 2 — API REST

```bash
poetry run python -m btime_rpa.run_api
```

O script consulta a AwesomeAPI e gera:

`data/api_exchange_rates.csv`

## Estrutura dos arquivos CSV

Ambos os arquivos utilizam o mesmo formato:

| Coluna | Descrição |
|---|---|
| currency | Moeda consultada (USD ou EUR) |
| base_currency | Moeda de referência (BRL) |
| rate | Cotação obtida |
| collected_at | Data e hora da coleta em ISO 8601 com fuso UTC |
| source | Fonte dos dados |

Exemplo ilustrativo:

```csv
currency,base_currency,rate,collected_at,source
USD,BRL,5.3441,2026-10-27T16:33:10.577933+00:00,AwesomeAPI
EUR,BRL,5.9555,2026-10-27T16:33:10.577951+00:00,AwesomeAPI
```

Os valores podem variar entre as fontes devido aos diferentes momentos e métodos de atualização das cotações.

## Tratamento de erros e robustez

A aplicação contempla:

- Tratamento de falhas HTTP e timeouts.
- Validação de dados recebidos.
- Tratamento de respostas inválidas.
- Retry com limite de tentativas no coletor Google Finance.
- Tratamento de erros de exportação.
- Logging das operações.
- Código de saída diferente de zero em caso de falha.

O scraping depende da estrutura HTML disponibilizada pelo Google Finance. Alterações nessa estrutura podem exigir ajustes no coletor.

A aplicação não tenta contornar CAPTCHA, autenticação ou restrições de acesso impostas pelas fontes.

## Testes automatizados

Execute:

```bash
poetry run pytest -v
```

Para executar com cobertura:

```bash
poetry run pytest -v --cov=btime_rpa --cov-report=term-missing
```

Resultado da última validação realizada:

- **49 testes aprovados**
- **99% de cobertura de código**
- **0 falhas**

Os testes abrangem componentes de domínio, casos de uso, adaptadores, exportação CSV e fluxos de integração.

## Entrega

O repositório contém os códigos-fonte dos dois métodos de coleta, testes automatizados e documentação.

Os arquivos CSV gerados devem ser incluídos na entrega para demonstrar o resultado das execuções.

## Considerações finais

A solução prioriza legibilidade, separação de responsabilidades, tratamento de falhas e facilidade de manutenção.

A utilização de um modelo comum para as cotações permite comparar os resultados obtidos por API e Web Scraping, mantendo o formato de saída consistente.