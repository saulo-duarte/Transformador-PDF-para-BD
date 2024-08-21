
  create view "Project_pdf_csv"."public"."bronze_fatura_jornada__dbt_tmp"
    
    
  as (
    WITH formatted AS (
    SELECT
        "n_nota" as n_nota,
        "cv",
        "merc",
        "tipo",
        TO_DATE("vecto", 'DDMMYYYY') AS vecto,
        CAST("qted" AS INT) AS qted,
        "mercadoria",
        CAST(REPLACE("cotacao", ',', '.') AS DECIMAL(10, 2)) AS cotacao,
        TO_DATE("data_de_pregao", 'DDMMYYYY') AS data_de_pregao,
        CAST(REPLACE("txop", ',', '.') AS DECIMAL(10, 2)) AS txop
    FROM
        "Project_pdf_csv"."public"."corretagem_jornada"
)

SELECT * 
FROM formatted
  );