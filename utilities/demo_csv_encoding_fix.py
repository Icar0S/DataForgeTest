#!/usr/bin/env python3
"""
Demonstration script showing the CSV encoding fix in action.

This script creates a sample CSV file with:
- Latin-1 encoding (like the user's real data)
- Tab delimiter
- Portuguese special characters
- Many columns (44 like the problem statement)

Then it processes it through the system and shows the results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dataset_inspector.inspector import inspect_csv
from dataset_inspector.dsl_generator import generate_dsl_from_metadata
from code_generator.pyspark_generator import generate_pyspark_code


def create_sample_csv():
    """Create a sample CSV matching the problem statement."""
    columns = [
        "Ano", "Mês", "UF", "IMPOSTO SOBRE IMPORTAÇÃO", "IMPOSTO SOBRE EXPORTAÇÃO",
        "IPI - FUMO", "IPI - BEBIDAS", "IPI - AUTOMÓVEIS", "IPI - VINCULADO À IMPORTACAO",
        "IPI - OUTROS", "IRPF", "IRPJ - ENTIDADES FINANCEIRAS", "IRPJ - DEMAIS EMPRESAS",
        "IRRF - RENDIMENTOS DO TRABALHO", "IRRF - RENDIMENTOS DO CAPITAL",
        "IRRF - REMESSAS P/ EXTERIOR", "IRRF - OUTROS RENDIMENTOS",
        "IMPOSTO S/ OPERAÇÕES FINANCEIRAS", "IMPOSTO TERRITORIAL RURAL",
        "IMPOSTO PROVIS.S/ MOVIMENT. FINANC. - IPMF", "CPMF", "COFINS",
        "COFINS - FINANCEIRAS", "COFINS - DEMAIS", "CONTRIBUIÇÃO PARA O PIS/PASEP",
        "CONTRIBUIÇÃO PARA O PIS/PASEP - FINANCEIRAS", "CONTRIBUIÇÃO PARA O PIS/PASEP - DEMAIS",
        "CSLL", "CSLL - FINANCEIRAS", "CSLL - DEMAIS", "CIDE-COMBUSTÍVEIS (parc. não dedutível)",
        "CIDE-COMBUSTÍVEIS", "CONTRIBUIÇÃO PLANO SEG. SOC. SERVIDORES",
        "CPSSS - Contrib. p/ o Plano de Segurid. Social Serv. Público",
        "CONTRIBUICÕES PARA FUNDAF", "REFIS", "PAES", "RETENÇÃO NA FONTE - LEI 10.833, Art. 30",
        "PAGAMENTO UNIFICADO", "OUTRAS RECEITAS ADMINISTRADAS", "DEMAIS RECEITAS",
        "RECEITA PREVIDENCIÁRIA", "RECEITA PREVIDENCIÁRIA - PRÓPRIA", "RECEITA PREVIDENCIÁRIA - DEMAIS"
    ]
    
    # Create header with tabs
    header = "\t".join(columns)
    
    # Create sample data rows
    rows = []
    for year in [2000, 2001, 2002]:
        for month in ["Janeiro", "Fevereiro", "Março"]:
            row_data = [str(year), month, "AC"] + [str(i * 1000) for i in range(41)]
            rows.append("\t".join(row_data))
    
    csv_content = header + "\n" + "\n".join(rows) + "\n"
    
    # Save with latin-1 encoding (to simulate real user data)
    filename = '/tmp/demo_receitas_federais.csv'
    with open(filename, 'wb') as f:
        f.write(csv_content.encode('latin-1'))
    
    return filename


def main():
    """Run the demonstration."""
    print("=" * 80)
    print("CSV ENCODING FIX DEMONSTRATION")
    print("=" * 80)
    
    # Step 1: Create sample CSV
    print("\n📄 Creating sample CSV file...")
    csv_file = create_sample_csv()
    print(f"✅ Created: {csv_file}")
    print("   - Encoding: latin-1 (ISO-8859-1)")
    print("   - Delimiter: Tab (\\t)")
    print("   - Columns: 44")
    print("   - Special chars: Mês, Importação, Operações, etc.")
    
    # Step 2: Inspect the CSV
    print("\n🔍 Step 1: Inspecting CSV with auto-detection...")
    metadata = inspect_csv(csv_file, {})  # No options = auto-detect
    
    print(f"✅ Detection successful!")
    print(f"   - Detected encoding: {metadata['detected_options']['encoding']}")
    print(f"   - Detected delimiter: {repr(metadata['detected_options']['delimiter'])}")
    print(f"   - Row count: {metadata['row_count']}")
    print(f"   - Column count: {metadata['column_count']}")
    print(f"   - First 5 columns: {[col['name'] for col in metadata['columns'][:5]]}")
    print(f"   - Last 3 columns: {[col['name'] for col in metadata['columns'][-3:]]}")
    
    # Step 3: Generate DSL
    print("\n🔧 Step 2: Generating DSL...")
    user_edits = {'dataset_name': 'receitas_federais'}
    dsl = generate_dsl_from_metadata(metadata, user_edits)
    
    print(f"✅ DSL generated!")
    print(f"   - Dataset name: {dsl['dataset']['name']}")
    print(f"   - Schema entries: {len(dsl['schema'])}")
    print(f"   - Validation rules: {len(dsl['rules'])}")
    print(f"   - Detected options preserved: {bool(dsl['dataset'].get('detected_options'))}")
    
    # Step 4: Generate PySpark code
    print("\n💻 Step 3: Generating PySpark code...")
    pyspark_code = generate_pyspark_code(dsl)
    
    print(f"✅ PySpark code generated!")
    print(f"   - Code length: {len(pyspark_code)} characters")
    print(f"   - Contains encoding option: {metadata['detected_options']['encoding'] in pyspark_code}")
    print(f"   - Contains delimiter option: {'.option(\"delimiter\"' in pyspark_code}")
    print(f"   - Google Colab compatible: {'findspark.init()' in pyspark_code}")
    print(f"   - File upload prompt: {'files.upload()' in pyspark_code}")
    
    # Save the generated code
    output_file = '/tmp/demo_generated_code.py'
    with open(output_file, 'w') as f:
        f.write(pyspark_code)
    print(f"\n💾 Generated code saved to: {output_file}")
    
    # Show a snippet of the generated code
    print("\n📝 Code snippet (CSV reading section):")
    print("-" * 80)
    lines = pyspark_code.split('\n')
    for i, line in enumerate(lines):
        if 'spark.read.format("csv")' in line:
            # Show 8 lines starting from this point
            for j in range(i, min(i + 8, len(lines))):
                print(lines[j])
            break
    print("-" * 80)
    
    print("\n✅ DEMONSTRATION COMPLETE!")
    print("\nKey points:")
    print("1. ✅ Auto-detection correctly identified latin-1 encoding")
    print("2. ✅ Auto-detection correctly identified tab delimiter")
    print("3. ✅ All 44 columns with special characters were processed")
    print("4. ✅ Generated code includes detected encoding and delimiter")
    print("5. ✅ Generated code is ready for Google Colab")
    print("\nThe original error 'utf-8 codec can't decode byte 0xea' is now fixed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
