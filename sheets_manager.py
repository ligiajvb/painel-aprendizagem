import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import time

load_dotenv()

class SheetsManager:
    """Gerenciador de integração com Google Sheets"""
    
    def __init__(self):
        self.spreadsheet = None
        self.data_dict = {}
        self._transformed_data = None
        self.is_connected = False
        self.last_update = None
        self._sync_in_progress = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializa a conexão com Google Sheets"""
        try:
            # Verifica se as variáveis de ambiente estão configuradas
            sheets_url = os.getenv('GOOGLE_SHEETS_URL')
            creds_file = os.getenv('SHEETS_CREDENTIALS_FILE', 'credentials.json')
            
            if not sheets_url:
                print("⚠ GOOGLE_SHEETS_URL não configurada - usando modo demo")
                self.is_connected = False
                self._load_demo_data()
                return
            
            # Tenta usar credenciais de ambiente primeiro (Vercel)
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            
            if credentials_json:
                # Usa credenciais da variável de ambiente
                import json
                creds_dict = json.loads(credentials_json)
                scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                print("✓ Usando credenciais do ambiente")
            elif os.path.exists(creds_file):
                # Usa arquivo de credenciais
                scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
                print(f"✓ Usando arquivo de credenciais: {creds_file}")
            else:
                print("⚠ Credenciais não encontradas - usando modo demo")
                self.is_connected = False
                self._load_demo_data()
                return
            
            # Conecta ao Google Sheets
            client = gspread.authorize(creds)
            sheet_id = self._extract_sheet_id(sheets_url)
            self.spreadsheet = client.open_by_key(sheet_id)
            self.is_connected = True
            print("✓ Conectado ao Google Sheets com sucesso!")
            
        except Exception as e:
            print(f"✗ Erro ao conectar ao Google Sheets: {e}")
            print("📊 Usando modo demo")
            self.is_connected = False
            self._load_demo_data()
    
    def _extract_sheet_id(self, url):
        """Extrai o ID da planilha da URL"""
        import re
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        raise ValueError("URL de planilha inválida")
    
    def _load_demo_data(self):
        """Carrega dados de demonstração"""
        print("📊 Carregando dados de demonstração...")
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
        """Sincroniza dados da planilha"""
        if not self.is_connected:
            print("📊 Usando dados de demonstração (modo offline)")
            return True
        
        if self._sync_in_progress:
            print("⏳ Sincronização já em andamento...")
            return False
        
        self._sync_in_progress = True
        
        try:
            worksheets = self.spreadsheet.worksheets()
            self.data_dict = {}
            
            for sheet in worksheets:
                sheet_name = sheet.title
                print(f"📄 Processando aba: {sheet_name}")
                
                all_values = sheet.get_all_values()
                if not all_values or len(all_values) < 2:
                    continue
                
                headers = all_values[0]
                sheet_data = {}
                
                for row_idx, row in enumerate(all_values[1:], 1):
                    row_dict = {}
                    for col_idx, header in enumerate(headers):
                        if col_idx < len(row):
                            row_dict[header] = row[col_idx]
                        else:
                            row_dict[header] = ""
                    
                    key = row[0] if row else f"row_{row_idx}"
                    sheet_data[key] = row_dict
                
                self.data_dict[sheet_name] = sheet_data
            
            self.last_update = time.time()
            self._transformed_data = None
            print(f"✓ Dados sincronizados! Total de abas: {len(worksheets)}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao sincronizar: {e}")
            return False
        finally:
            self._sync_in_progress = False
    
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
            if not isinstance(row_data, dict):
                continue
            
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
            "connected": self.is_connected,
            "last_update": self.last_update,
            "data_sheets": len(self.data_dict),
            "total_records": sum(len(sheet) for sheet in self.data_dict.values()),
            "mode": "demo" if not self.is_connected else "live"
        }

# Instância global
sheets_manager = SheetsManager()
