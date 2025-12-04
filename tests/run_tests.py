"""
Script para ejecutar todas las pruebas del proyecto Sudoku
Ejecuta pruebas unitarias y de integración con reportes detallados
"""

import unittest
import sys
import os
from datetime import datetime

# Asegura que el directorio tests esté en el path
sys.path.insert(0, os.path.dirname(__file__))

# Importa los módulos de prueba
import test_logica_sudoku
import test_generador_tableros
import test_gestor_puntuaciones
import test_integracion


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Imprime una sección formateada"""
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70)


def run_test_suite(suite_name, test_module):
    """
    Ejecuta una suite de pruebas y retorna los resultados
    
    Args:
        suite_name: Nombre de la suite para mostrar
        test_module: Módulo que contiene las pruebas
    
    Returns:
        TestResult: Resultado de la ejecución
    """
    print_section(suite_name)
    
    # Crea la suite de pruebas
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_module)
    
    # Ejecuta las pruebas con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


def print_summary(results):
    """
    Imprime un resumen de todos los resultados
    
    Args:
        results: Lista de tuplas (nombre, TestResult)
    """
    print_header("RESUMEN DE RESULTADOS")
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    
    print("\nResultados por suite:")
    print("-" * 70)
    
    for name, result in results:
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
        
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        total_skipped += skipped
        
        # Determina el estado
        if failures == 0 and errors == 0:
            status = "✓ PASÓ"
            status_symbol = "✓"
        else:
            status = "✗ FALLÓ"
            status_symbol = "✗"
        
        print(f"{status_symbol} {name:40} | Tests: {tests_run:3} | "
              f"Fallos: {failures:2} | Errores: {errors:2}")
    
    print("-" * 70)
    print(f"\nTOTAL DE PRUEBAS EJECUTADAS: {total_tests}")
    print(f"  • Exitosas: {total_tests - total_failures - total_errors}")
    print(f"  • Fallidas:  {total_failures}")
    print(f"  • Errores:   {total_errors}")
    if total_skipped > 0:
        print(f"  • Omitidas:  {total_skipped}")
    
    # Resultado final
    print("\n" + "=" * 70)
    if total_failures == 0 and total_errors == 0:
        print("  ✓✓✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE ✓✓✓")
        print("=" * 70)
        return True
    else:
        print(f"  ✗✗✗ {total_failures + total_errors} PRUEBA(S) FALLARON ✗✗✗")
        print("=" * 70)
        return False


def main():
    """Función principal que ejecuta todas las pruebas"""
    print_header("EJECUCIÓN DE PRUEBAS AUTOMATIZADAS - SUDOKU 9x9")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de suites de prueba
    test_suites = [
        ("Pruebas Unitarias - Lógica Sudoku", test_logica_sudoku),
        ("Pruebas Unitarias - Generador de Tableros", test_generador_tableros),
        ("Pruebas Unitarias - Gestor de Puntuaciones", test_gestor_puntuaciones),
        ("Pruebas de Integración", test_integracion),
    ]
    
    # Ejecuta cada suite y guarda los resultados
    results = []
    for suite_name, test_module in test_suites:
        result = run_test_suite(suite_name, test_module)
        results.append((suite_name, result))
    
    # Imprime el resumen
    success = print_summary(results)
    
    # Retorna código de salida apropiado
    return 0 if success else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
