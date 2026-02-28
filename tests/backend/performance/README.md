# Testes de Performance e Carga — DataForgeTest

## Benchmarks Locais (sem rede)
```bash
pytest tests/backend/performance/test_performance_benchmarks.py -v --benchmark-json=results/benchmark.json
```

## SLAs de Produção (requer backend online)
```bash
RUN_PRODUCTION_TESTS=true pytest tests/backend/performance/test_sla_production.py -v
```

## Testes de Carga com Locust (UI)
```bash
locust -f tests/backend/performance/locustfile.py --host=https://dataforgetest-backend.onrender.com
```

## Testes de Carga Headless (CI)
```bash
locust -f tests/backend/performance/locustfile.py \
  --host=https://dataforgetest-backend.onrender.com \
  --headless \
  --users=10 \
  --spawn-rate=2 \
  --run-time=60s \
  --html=results/load_test_report.html
```

## SLAs Definidos
| Endpoint                    | SLA Local | SLA Produção |
|-----------------------------|-----------|--------------|
| GET /                       | < 50ms    | < 2s (warm)  |
| POST /ask                   | < 200ms*  | < 30s        |
| POST /api/metrics/analyze   | < 2s      | < 15s        |
| POST /api/dataset_inspector | < 3s      | < 20s        |
| POST /api/synth/generate    | < 1s*     | < 45s        |
| POST /api/rag/chat          | < 500ms*  | < 20s        |

*Sem LLM (mock/local)
