# Estratégias de Validação de Dados

## Validação em Tempo Real vs Batch

### Validação Batch
- Processa grandes volumes de dados históricos
- Permite análises complexas e estatísticas
- Ideal para relatórios e auditorias
- Menos recursos em tempo real

### Validação em Tempo Real
- Verifica dados conforme chegam
- Permite correção imediata
- Requer mais recursos de infraestrutura
- Crítica para sistemas transacionais

## Implementação com Kafka + Spark Streaming

```python
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def process_streaming_data(df, epoch_id):
    # Validações em tempo real
    
    # 1. Schema validation
    expected_schema = ["id", "timestamp", "value", "status"]
    if set(df.columns) != set(expected_schema):
        raise ValueError("Schema mismatch detected")
    
    # 2. Business rules validation
    invalid_records = df.filter(
        (col("value") < 0) | 
        (col("value") > 1000) |
        (col("status").isNull())
    )
    
    invalid_count = invalid_records.count()
    if invalid_count > 0:
        print(f"Warning: {invalid_count} invalid records found")
        # Log para sistema de monitoramento
    
    # 3. Store valid records
    valid_records = df.subtract(invalid_records)
    valid_records.write.mode("append").saveAsTable("clean_data")

# Setup streaming
spark = SparkSession.builder.appName("DataQualityStream").getOrCreate()
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "data-topic") \
    .load()

query = df.writeStream \
    .foreachBatch(process_streaming_data) \
    .start()

query.awaitTermination()
```

## Padrões de Quarentena

### Isolamento de Dados Problemáticos
1. **Quarentena Automática**: Dados que falham validação básica
2. **Quarentena Manual**: Dados suspeitos para revisão humana
3. **Quarentena Temporária**: Dados aguardando informações adicionais

### Estrutura de Quarentena
```
quarantine/
├── schema_errors/
├── business_rule_violations/
├── data_quality_issues/
└── pending_review/
```

## Métricas de Qualidade

- **Completude**: % de campos preenchidos
- **Validade**: % de dados em formato correto
- **Consistência**: % de dados consistentes entre fontes
- **Precisão**: % de dados corretos
- **Atualidade**: % de dados recentes