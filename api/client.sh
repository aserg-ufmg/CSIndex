echo  1: Número de publicações em uma determinada conferência de uma área
echo  Area: Inteligencia Artifical e Conferencia: GECCO
curl -i http://localhost:5000/numeroPublicacoesConferenciaArea/ai/GECCO
echo  Area: Mineracao de Dados e Conferencia: ECML/PKDD
curl -i http://localhost:5000/numeroPublicacoesConferenciaArea/data/ECML/PKDD
echo ---------------------------------------------------------------------------
echo  2: Número de publicações no conjunto de conferências de uma área
echo  Area: Arquitetura
printf "\n"
curl -i http://localhost:5000/numeroPublicacoesArea/arch
echo  Area: Visao Computacional
printf "\n"
curl -i http://localhost:5000/numeroPublicacoesArea/vision
echo ---------------------------------------------------------------------------
echo  3: Scores de todos os departamentos em uma área
echo  Area: Interacao Humano Computador
curl -i http://localhost:5000/scoreTodosDepartamentosArea/chi
echo ---------------------------------------------------------------------------
echo  4: Score de um determinado departamento em uma área.
echo  Area: Engenharia de Software e Departamento: UFMG
curl -i http://localhost:5000/scoreDepartamentoArea/se/UFMG
echo  Area: Banco de Dados e Departamento: PUC-Rio
curl -i http://localhost:5000/scoreDepartamentoArea/db/PUC-Rio
echo ---------------------------------------------------------------------------
echo  5: Número de professores que publicam em uma determinada área
echo  Area: Inteligencia Artificial
curl -i http://localhost:5000/numeroProfessoresAreaAgrupadoDepartamento/ai
echo  Area: Visao Computacional
curl -i http://localhost:5000/numeroProfessoresAreaAgrupadoDepartamento/vision
echo ---------------------------------------------------------------------------
echo  6: Número de professores de um determinado departamento que publicam em uma área
echo  Area: Mineracao de Dados e Departamento: UFMG
curl -i http://localhost:5000/numeroProfessoresDepartamentoArea/data/UFMG
echo  Area: Banco de Dados e Departamento: ICMC/USP
curl -i http://localhost:5000/numeroProfessoresDepartamentoArea/db/ICMC/USP
echo ---------------------------------------------------------------------------
echo  7: Todos os papers de uma área 
echo  Area: Arquitetura
curl -i http://localhost:5000/papersArea/arch
echo  Area: Interacao Humano Computador
curl -i http://localhost:5000/papersArea/chi
echo ---------------------------------------------------------------------------
echo  8: Todos os papers de uma área em um determinado ano
echo  Area: Mineracao de Dados e Ano: 2013
curl -i http://localhost:5000/papersAreaAno/data/2013
echo  Area: Banco de Dados e Ano: 2017
curl -i http://localhost:5000/papersAreaAno/data/2017
echo ---------------------------------------------------------------------------
echo  9: Todos os papers de um departamento em uma área
echo  Area: Banco de Dados e Departamento: UFMG
curl -i http://localhost:5000/papersAreaDepartamento/db/UFMG
echo  Area: Inteligencia Artificial e Departamento: IME/USP
curl -i http://localhost:5000/papersAreaDepartamento/ai/IME/USP
echo ---------------------------------------------------------------------------
echo  10: Todos os papers de um professor
echo  Professor: Renato Assuncao
curl -i http://localhost:5000/papersProfessor/Renato-Assuncao
echo  Professor: Rodrygo Santos
curl -i http://localhost:5000/papersProfessor/Rodrygo-Santos