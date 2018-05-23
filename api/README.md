# API REST
API desenvolvida para a disciplina de Engenharia de Software 2.

## Desenvolvedores

André Correia Lacerda Mafra
Felipe Giori

## Requisitos
Linguagem: python 2.7
As bibliotecas pandas e flask foram usadas na API. Para instalar as bibliotecas use of comandos em seu terminal: 
```
pip install pandas
pip install Flask
```

## Áreas
| Área | String |
| ------| :----: |
|Software Engineering|se|
|Programming Languages|pl|
|Information Systems|is|
|Human-Computer Interaction|chi|
|Computer Networks|net|
|Mobile Computing|mobile|
|Distributed Systems|ds|
|Computer Architecture & HPC|arch|
|Databases|db|
|Web & Information Retrieval|ir|
|Data Mining & Machine Learning|data|
|Artificial Intelligence|ai|
|Algorithms & Complexity|theory|
|Security & Cryptography|security|
|Computer Vision|vision|
|Formal Methods & Logic|formal|
## Funções
Os valores em negrito devem as ser entradas de uma chamada.

| Paramethers       | Method          | Path  | Format |
| ------------- |:-------------:|:-----:|:-----:|
| area, conferencia | GET | /numeroPublicacoesConferenciaArea/**area**/**conferencia** | CSV |
| area | GET | /numeroPublicacoesArea/**area** | CSV |
| area | GET | /scoreTodosDepartamentosArea/**area** | CSV |
|area, departamento|GET|/scoreDepartamentoArea/**area**/**departamento**|CSV|
|area|GET|/numeroProfessoresAreaAgrupadoDepartamento/**area**|CSV|
|area, departamento|GET|/numeroProfessoresDepartamentoArea/**area**/**departamento**|CSV|
|area|GET|/papersArea/**area**|CSV|
|area, ano|GET|/papersAreaAno/**area**/**ano**|CSV|
|area, departamento|GET|/papersAreaDepartamento/**area**/**departamento**|CSV|
|professor|GET|/papersProfessor/**professor**|CSV|

### Exemplo de execução:
Exemplo de endereço que retorna o score de todos os departamentos da área de Data mining & Machine Learning.
```
http://localhost:5000/scoreTodosDepartamentosArea/data
```
O resultado é um arquivo .csv com o seguinte conteúdo:

| Departamento | Score |
|----------|:-------:|
|ICMC/USP|7.29|
|UFMG|4.64|
|UFRJ|1.33|
|PUC-Rio|1.0|
|UFF|0.66|
|UFPE|0.66|
|PUC-PR|0.33|
|PUC-RS|0.33|
|UFCG|0.33|
|UFSCAR|0.33|
|UFSJ|0.33|
|UNIFOR|0.33|
