import pandas as pd
from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# No Render, o banco de dados não estará acessível
# Portanto, usaremos dados de exemplo ou um arquivo CSV/Excel

def obter_dados_fila():
    """
    Obtém os dados da tabela Fila.
    No Render, tenta ler de um arquivo CSV/Excel local.
    Se não existir, usa dados de exemplo.
    """
    
    # Tentativa 1: Ler de um arquivo Excel/CSV na pasta do projeto
    try:
        # Procura por um arquivo Excel na pasta
        for arquivo in os.listdir('.'):
            if arquivo.endswith('.xlsx') or arquivo.endswith('.csv'):
                if arquivo.endswith('.xlsx'):
                    df = pd.read_excel(arquivo)
                else:
                    df = pd.read_csv(arquivo)
                
                # Normaliza os nomes das colunas para minúsculas
                df.columns = [col.lower().strip() for col in df.columns]
                return df
    except Exception as e:
        print(f"Erro ao ler arquivo local: {e}")
    
    # Se tudo falhar, retornar dados de exemplo
    print("Usando dados de exemplo (nenhum arquivo encontrado)")
    return criar_dados_exemplo()

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstração."""
    dados = {
        'ref': ['SL4415', 'SL4416', 'SL4417', 'SL4418', 'SL4419', 'SL4420'],
        'descricao': [
            'SUPORTE PARA PAINEL ELETROELETRÔNICO SWD',
            'SUPORTE PARA PAINEL ELETROELETRÔNICO SWD',
            'SUPORTE PARA PAINEL ELETROELETRÔNICO SWD',
            'SUPORTE PARA PAINEL ELETROELETRÔNICO SWD',
            'SUPORTE PARA PAINEL ELETROELETRÔNICO SWD',
            'SUPORTE PARA PAINEL ELETROELETRÔNICO SWD'
        ],
        'solicitante': ['VITOR RIBEIRO', 'VITOR RIBEIRO', 'VITOR RIBEIRO', 'VITOR RIBEIRO', 'VITOR RIBEIRO', 'VITOR RIBEIRO'],
        'cod_z': ['Z3156', 'Z3157', 'Z3158', 'Z3159', 'Z3160', 'Z3161'],
        'aplicacao': ['SOLID-JONATAN', 'SOLID-JONATAN', 'SOLID-JONATAN', 'SOLID-JONATAN', 'SOLID-JONATAN', 'SOLID-JONATAN'],
        'vagao': ['HTT', 'HTT', 'HTT', 'HTT', 'HTT', 'HTT'],
        'conceito_p': ['PINTURA', 'PINTURA', 'PINTURA', 'SOLDAGEM', 'PINTURA', 'SOLDAGEM'],
        'conceito_st': ['PENDENTE', 'PENDENTE', 'EM ANDAMENTO', 'CONCLUÍDO', 'PENDENTE', 'EM ANDAMENTO'],
        'conceito_ini': ['07.10.25', '07.10.25', '08.10.25', '08.10.25', '09.10.25', '09.10.25'],
        'conceito_fim': ['08.10.25', '08.10.25', '09.10.25', '10.10.25', '10.10.25', '11.10.25']
    }
    return pd.DataFrame(dados)

def obter_opcoes_filtro(coluna):
    """Obtém as opções únicas de uma coluna para usar nos filtros dropdown."""
    df = obter_dados_fila()
    if df is None or coluna not in df.columns:
        return []
    
    opcoes = sorted(df[coluna].dropna().unique().tolist())
    return opcoes

# --- ROTAS ---

@app.route('/')
def index():
    """Página principal com a tabela e filtros."""
    df = obter_dados_fila()
    
    if df is None:
        return "Erro ao conectar ao banco de dados", 500
    
    # Obtém as opções para os filtros dropdown
    conceito_p_opcoes = obter_opcoes_filtro('conceito_p')
    conceito_st_opcoes = obter_opcoes_filtro('conceito_st')
    
    # Converte o DataFrame para JSON para passar ao template
    dados_json = df.to_json(orient='records', date_format='iso')
    
    return render_template('index.html',
                         dados_json=dados_json,
                         conceito_p_opcoes=conceito_p_opcoes,
                         conceito_st_opcoes=conceito_st_opcoes,
                         timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

@app.route('/api/dados')
def api_dados():
    """API que retorna os dados em JSON."""
    df = obter_dados_fila()
    
    if df is None:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500
    
    # Converte para JSON
    dados = df.to_dict(orient='records')
    
    return jsonify({
        "dados": dados,
        "timestamp": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    })

@app.route('/api/detalhe/<int:index>')
def api_detalhe(index):
    """API que retorna os detalhes de uma linha específica."""
    df = obter_dados_fila()
    
    if df is None:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500
    
    if index < 0 or index >= len(df):
        return jsonify({"erro": "Índice inválido"}), 404
    
    # Obtém a linha específica
    linha = df.iloc[index]
    detalhe = linha.to_dict()
    
    return jsonify(detalhe)

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    # No Render, a porta é definida pela variável de ambiente PORT
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("  SL VIEWER - Iniciando Servidor")
    print("=" * 60)
    print(f"Servidor rodando na porta {port}")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=port)
