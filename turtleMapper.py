import csv
import os
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD, RDFS

EX = Namespace("http://example.org/health/")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")
ICD = Namespace("http://purl.bioontology.org/ontology/ICD10/")

SEXO_MAP = {
    "Feminino": DBR["Female"],
    "Masculino": DBR["Male"]
}

UF_MAP = {
    "RO": DBR["Rondonia"],
}

g = Graph()
g.bind("ex", EX)
g.bind("dbo", DBO)
g.bind("dbr", DBR)
g.bind("icd", ICD)
g.bind("rdfs", RDFS)

PATH = "./assets/sanitized/csv"

for ano in ['2022', '2023', '2024']:
    for trimestre in ['01', '02', '03']:
        prefixo = f"RO_{ano}{trimestre}"
        
        for arquivo in os.listdir(PATH):
            if arquivo.startswith(prefixo) and arquivo.endswith(".csv"):
                caminho = os.path.join(PATH, arquivo)
                print(f"Lendo: {arquivo}")

                with open(caminho, newline='', encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=';')
                    for row in reader:
                        evento_uri = EX["evento" + row["ID_EVENTO_ATENCAO_SAUDE"]]
                        g.add((evento_uri, RDF.type, DBO.MedicalProcedure))
                        g.add((evento_uri, DBO.ageRange, Literal(row["FAIXA_ETARIA"])))
                        g.add((evento_uri, EX.ano, Literal(ano, datatype=XSD.gYear)))
                        g.add((evento_uri, EX.mes, Literal(trimestre, datatype=XSD.gMonth)))
                        g.add((evento_uri, DBO.sex, SEXO_MAP.get(row["SEXO"], Literal(row["SEXO"]))))
                        g.add((evento_uri, DBO.region, UF_MAP.get(row["UF_PRESTADOR"], Literal(row["UF_PRESTADOR"]))))
                        g.add((evento_uri, DBO.duration, Literal(int(row["TEMPO_DE_PERMANENCIA"]), datatype=XSD.integer)))
                        g.add((evento_uri, EX.porte, Literal(row["PORTE"])))
                        g.add((evento_uri, DBO.disease, ICD[row["CID_1"]]))
                        g.add((evento_uri, EX.municipioBeneficiario, Literal(row["CD_MUNICIPIO_BENEFICIARIO"])))

g.serialize("eventos.ttl", format="turtle")
print("Arquivo 'eventos.ttl' gerado com sucesso.")
