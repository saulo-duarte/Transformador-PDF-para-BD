
  create view "Project_pdf_csv"."public"."bronze_fatura_jornada_small__dbt_tmp"
    
    
  as (
    WITH formatted AS (
    SELECT
        n_nota,
        TO_DATE("data_de_pregao", 'DDMMYYYY') AS data_de_pregao,
        CAST(REPLACE("corretagem", ',', '.') AS DECIMAL(10, 2)) AS tx_corretagem,
        CAST(REPLACE("taxa_de_registro", ',', '.') AS DECIMAL(10, 2)) AS taxa
    FROM
        "Project_pdf_csv"."public"."corretagem_jornada_small"
)

SELECT * 
FROM formatted
  );