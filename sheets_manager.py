import os
import time

class SheetsManager:
    """Gerenciador de integração com Google Sheets"""
    
    def __init__(self):
        self.data_dict = {}
        self._transformed_data = None  # Cache para dados transformados
        self.is_connected = False
        self.last_update = None
        self._sync_in_progress = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializa a conexão com Google Sheets"""
        try:
            # Sempre usa modo demo para evitar erros na Vercel
            print("🌐 Usando modo demo para evitar erros de deploy")
            self.is_connected = False
            self._load_demo_data()
        except Exception as e:
            print(f"✗ Erro na inicialização: {e}")
            self.is_connected = False
            self._load_demo_data()
    
    def _load_demo_data(self):
        """Carrega dados de demonstração quando não há conexão com Google Sheets"""
        print("📊 Carregando dados de demonstração...")
        
        # Dados demo no formato esperado pelo frontend
        self.data_dict = {
            'Resumo_Por_Turma': {
                'DEMO_1A_Q1': {
                    'AvaliacaoID': 'DEMO_LP_5ANO',
                    'TurmaID': '5A',
                    'QuestaoID': 'Q_1',
                    '%Acerto': '75%',
                    'TotalRespostas': '20',
                    'TotalAcertos': '15',
                    'Habilidade': 'EF05LP10',
                    'Descritor': 'Reconhecer o efeito de humor em textos'
                },
                'DEMO_1A_Q2': {
                    'AvaliacaoID': 'DEMO_LP_5ANO',
                    'TurmaID': '5A',
                    'QuestaoID': 'Q_2',
                    '%Acerto': '60%',
                    'TotalRespostas': '20',
                    'TotalAcertos': '12',
                    'Habilidade': 'EF35LP06',
                    'Descritor': 'Recuperar o sentido do texto'
                },
                'DEMO_1B_Q1': {
                    'AvaliacaoID': 'DEMO_LP_5ANO',
                    'TurmaID': '5B',
                    'QuestaoID': 'Q_1',
                    '%Acerto': '85%',
                    'TotalRespostas': '20',
                    'TotalAcertos': '17',
                    'Habilidade': 'EF05LP10',
                    'Descritor': 'Reconhecer o efeito de humor em textos'
                },
                'DEMO_1B_Q2': {
                    'AvaliacaoID': 'DEMO_LP_5ANO',
                    'TurmaID': '5B',
                    'QuestaoID': 'Q_2',
                    '%Acerto': '70%',
                    'TotalRespostas': '20',
                    'TotalAcertos': '14',
                    'Habilidade': 'EF35LP06',
                    'Descritor': 'Recuperar o sentido do texto'
                }
            }
        }
        
        self.last_update = time.time()
        self._transformed_data = None
        print("✓ Dados de demonstração carregados!")
    
    def sync_data(self):
        """Sincroniza dados (modo demo apenas)"""
        print("📊 Usando dados de demonstração (modo offline)")
        return True
    
    def get_sheet_data(self, sheet_name):
        """Retorna dados de uma aba específica"""
        return self.data_dict.get(sheet_name, {})
    
    def get_all_data(self):
        """Retorna todos os dados transformados para o formato esperado pelo frontend"""
        # Usa cache se disponível
        if self._transformed_data is not None:
            return self._transformed_data
        
        # Transforma e cacheia os dados
        self._transformed_data = self._transform_data_for_frontend()
        return self._transformed_data
    
    def _transform_data_for_frontend(self):
        """Transforma dados do Sheets para o formato esperado pelo frontend"""
        transformed = {}
        
        # Usa a aba Resumo_Por_Turma que contém os dados formatados
        resumo_data = self.data_dict.get('Resumo_Por_Turma', {})
        
        for key, row_data in resumo_data.items():
            if not isinstance(row_data, dict):
                continue
                
            # Extrai informações do chave e dos dados
            avaliacao_id = row_data.get('AvaliacaoID', '')
            turma_id = row_data.get('TurmaID', '')
            questao_id = row_data.get('QuestaoID', '')
            
            if not all([avaliacao_id, turma_id, questao_id]):
                continue
            
            # Inicializa estruturas se necessário
            if avaliacao_id not in transformed:
                transformed[avaliacao_id] = {}
            if turma_id not in transformed[avaliacao_id]:
                transformed[avaliacao_id][turma_id] = {}
            
            # Transforma para o formato esperado
            transformed[avaliacao_id][turma_id][questao_id] = {
                'pct': float(row_data.get('%Acerto', '0%').replace('%', '')),
                'total': int(row_data.get('TotalRespostas', '0')),
                'acertos': int(row_data.get('TotalAcertos', '0')),
                'habilidade': row_data.get('Habilidade', ''),
                'descritor': row_data.get('Descritor', '')
            }
        
        return transformed
    
    def start_auto_sync(self, interval_seconds=300):
        """Inicia sincronização automática (desativado em modo demo)"""
        print("✓ Modo demo - sincronização automática desativada")
    
    def get_status(self):
        """Retorna status da conexão"""
        return {
            "connected": self.is_connected,
            "last_update": self.last_update,
            "data_sheets": len(self.data_dict),
            "total_records": sum(len(sheet) for sheet in self.data_dict.values()),
            "mode": "demo"
        }


# Instância global
sheets_manager = SheetsManager()
