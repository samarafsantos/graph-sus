# Graph-SUS

Este é o projeto final da disciplina de Web Semântica, que utiliza grafos de conhecimento para analisar dados relacionados ao SUS (Sistema Único de Saúde) e ANS (Agência Nacional de Saúde Suplementar).

## Estrutura do Projeto

- **`app.py`**: Código principal da aplicação Streamlit para visualização e análise dos dados.
- **`eventos.ttl`**: Arquivo RDF contendo os dados semânticos em formato Turtle.
- **`requirements.txt`**: Lista de dependências necessárias para executar o projeto.

## Funcionalidades

1. **Consulta Avançada**:
   - Permite realizar consultas SPARQL personalizadas sobre os dados RDF.
2. **Análise Temporal**:

   - Visualização de dados agrupados por períodos de tempo (ano e mês).

3. **Drill-Down**:

   - Navegação detalhada por categorias como sexo, faixa etária, CID, e porte.

4. **Distribuição por Categoria**:

   - Gráficos de distribuição por atributos como sexo, faixa etária, CID, e porte.

5. **Grafo Interativo**:
   - Visualização de grafos interativos mostrando relações entre eventos médicos e seus atributos.

## Como Executar

1. Clone o repositório:

   ```bash
   git clone https://github.com/samarafsantos/graph-sus.git
   ```

2. Configure o ambiente virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## Dependências

As principais dependências do projeto incluem:

- **Streamlit**: Para criar a interface interativa.
- **SPARQLWrapper**: Para realizar consultas SPARQL.
- **Pandas**: Para manipulação de dados.
- **Matplotlib**: Para visualização gráfica.
- **PyVis**: Para visualização de grafos interativos.
- **NetworkX**: Para manipulação de grafos.

Todas as dependências estão listadas no arquivo `requirements.txt`.

## Dados RDF

Os dados estão armazenados no arquivo `eventos.ttl` e seguem os padrões semânticos utilizando os seguintes prefixos:

- `dbo`: Ontologia da DBpedia.
- `dbr`: Recursos da DBpedia.
- `ex`: Extensão personalizada para o projeto.
- `icd`: Ontologia do CID-10.
- `xsd`: Tipos de dados XML Schema.

### Observações

- Certifique-se de que o endpoint SPARQL está configurado corretamente no arquivo `app.py`:
  (Para funcionar é necessário configurar o GraphDb com o arquivo de eventos.ttl)
  ```python
  sparql = SPARQLWrapper("http://localhost:7200/repositories/Trab-final")
  ```
- Para melhor desempenho, o grafo interativo limita a visualização a 50 eventos.

Se tiver dúvidas ou problemas, entre em contato!
