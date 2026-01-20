import unicodedata

def debug_norm_detalhe():
    """Debug detalhado da normalização"""
    
    print("=== DEBUG DETALHADO DA NORMALIZAÇÃO ===")
    
    def _norm_txt(x: object) -> str:
        s = "" if x is None else str(x)
        print(f"Original: '{s}'")
        s_normalizado = unicodedata.normalize("NFKD", s)
        print(f"NFKD: '{s_normalizado}'")
        s_ascii = s_normalizado.encode("ascii", "ignore").decode("ascii")
        print(f"ASCII: '{s_ascii}'")
        s_final = s_ascii.strip().lower()
        print(f"Final: '{s_final}'")
        print("---")
        return s_final
    
    # Testar com os valores do problema
    test_values = ["Auto/RE", "Saúde", "Câmbio", "Seguros"]
    
    for val in test_values:
        print(f"Processando: {val}")
        resultado = _norm_txt(val)
        print(f"Resultado: '{resultado}'")
        print("=" * 50)

if __name__ == "__main__":
    debug_norm_detalhe()
