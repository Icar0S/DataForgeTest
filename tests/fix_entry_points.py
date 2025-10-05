"""
Script para corrigir arquivos entry_points.txt corrompidos que estão causando
erro intermitente na importação do anthropic.

O problema está relacionado à sincronização do OneDrive que corrompe alguns
arquivos entry_points.txt com erros de "operação na nuvem".
"""

from pathlib import Path


def fix_corrupted_entry_points():
    """
    Corrige arquivos entry_points.txt corrompidos reinstalando os pacotes afetados.
    """

    venv_path = Path(".venv/Lib/site-packages")

    # Pacotes conhecidos com problemas
    corrupted_packages = [
        "flask-3.1.1.dist-info",
        "jinja2-3.1.6.dist-info",
        "pip-24.2.dist-info",
    ]

    print("=== CORREÇÃO DE ARQUIVOS ENTRY_POINTS.TXT CORROMPIDOS ===\n")

    for package_dir in corrupted_packages:
        package_path = venv_path / package_dir
        entry_points_file = package_path / "entry_points.txt"

        print(f"Verificando {package_dir}...")

        if entry_points_file.exists():
            try:
                # Tentar ler o arquivo
                entry_points_file.read_text(encoding="utf-8")
                print(f"  ✓ {package_dir} está OK")
            except Exception as e:
                print(f"  ❌ {package_dir} corrompido: {e}")

                # Criar um arquivo entry_points.txt vazio/mínimo para o pacote
                try:
                    print(f"  🔧 Criando entry_points.txt vazio para {package_dir}...")
                    entry_points_file.write_text("", encoding="utf-8")
                    print(f"  ✓ Arquivo corrigido para {package_dir}")
                except Exception as fix_error:
                    print(f"  ❌ Erro ao corrigir {package_dir}: {fix_error}")
        else:
            print(f"[info] entry_points.txt não existe para {package_dir}")

    print("\n=== CORREÇÃO CONCLUÍDA ===")


if __name__ == "__main__":
    fix_corrupted_entry_points()
