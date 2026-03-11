# Gerenciador simplificado para Vercel
class SheetsManager:
    """Gerenciador de dados para o Painel de Aprendizagem"""
    
    def __init__(self):
        self.data_dict = {}
        self._transformed_data = None
        self.is_connected = False
        self.last_update = None
        self._load_demo_data()
    
    def _load_demo_data(self):
        """Carrega dados de demonstração"""
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
        self._transformed_data = None
    
    def sync_data(self):
        """Sincroniza dados (sempre sucesso em modo demo)"""
        return True
    
    def get_sheet_data(self, sheet_name):
        """Retorna dados de uma aba específica"""
        return self.data_dict.get(sheet_name, {})
    
    def get_all_data(self):
        """Retorna todos os dados transformados"""
        if self._transformed_data is not None:
            return self._transformed_data
        
        self._transformed_data = self._transform_data_for_frontend()
        return self._transformed_data
    
    def _transform_data_for_frontend(self):
        """Transforma dados para o formato do frontend"""
        transformed = {}
        resumo_data = self.data_dict.get('Resumo_Por_Turma', {})
        
        for key, row_data in resumo_data.items():
            avaliacao_id = row_data.get('AvaliacaoID', '')
            turma_id = row_data.get('TurmaID', '')
            questao_id = row_data.get('QuestaoID', '')
            
            if not all([avaliacao_id, turma_id, questao_id]):
                continue
            
            if avaliacao_id not in transformed:
                transformed[avaliacao_id] = {}
            if turma_id not in transformed[avaliacao_id]:
                transformed[avaliacao_id][turma_id] = {}
            
            transformed[avaliacao_id][turma_id][questao_id] = {
                'pct': float(row_data.get('%Acerto', '0%').replace('%', '')),
                'total': int(row_data.get('TotalRespostas', '0')),
                'acertos': int(row_data.get('TotalAcertos', '0')),
                'habilidade': row_data.get('Habilidade', ''),
                'descritor': row_data.get('Descritor', '')
            }
        
        return transformed
    
    def start_auto_sync(self, interval_seconds=300):
        """Inicia sincronização automática (desativado)"""
        pass
    
    def get_status(self):
        """Retorna status da conexão"""
        return {
            "connected": False,
            "last_update": None,
            "data_sheets": len(self.data_dict),
            "total_records": sum(len(sheet) for sheet in self.data_dict.values()),
            "mode": "demo"
        }

# Instância global
sheets_manager = SheetsManager()
