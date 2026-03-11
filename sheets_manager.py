import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import json
from threading import Thread
import time

load_dotenv()

class SheetsManager:
    """Gerenciador de integração com Google Sheets"""
    
    def __init__(self):
        self.spreadsheet = None
        self.data_dict = {}
        self._transformed_data = None  # Cache para dados transformados
        self.is_connected = False
        self.last_update = None
        self._sync_in_progress = False  # Evita sincronizações simultâneas
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializa a conexão com Google Sheets"""
        try:
            # Se houver arquivo de credenciais, use-o
            creds_file = os.getenv('SHEETS_CREDENTIALS_FILE', 'credentials.json')
            
            if os.path.exists(creds_file):
                scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
                
                client = gspread.authorize(creds)
                sheets_url = os.getenv('GOOGLE_SHEETS_URL')
                
                # Extrai o ID da planilha da URL
                sheet_id = self._extract_sheet_id(sheets_url)
                self.spreadsheet = client.open_by_key(sheet_id)
                self.is_connected = True
                print("✓ Conectado ao Google Sheets com sucesso!")
                # Não sincroniza automaticamente na inicialização
            else:
                print("⚠ Arquivo credentials.json não encontrado.")
                print("Para integração com Google Sheets, siga estes passos:")
                print("1. Acesse: https://console.cloud.google.com/")
                print("2. Crie um novo projeto")
                print("3. Ative a Google Sheets API")
                print("4. Crie uma conta de serviço e baixe o JSON")
                print("5. Renomeie para 'credentials.json' na raiz do projeto")
                self.is_connected = False
        except Exception as e:
            print(f"✗ Erro ao conectar ao Google Sheets: {e}")
            self.is_connected = False
    
    def _extract_sheet_id(self, url):
        """Extrai o ID da planilha da URL"""
        import re
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        raise ValueError("URL de planilha inválida")
    
    def sync_data(self):
        """Sincroniza dados da planilha para o dicionário"""
        # Evita sincronizações simultâneas
        if self._sync_in_progress:
            print("⏳ Sincronização já em andamento, aguardando...")
            return False
            
        if not self.is_connected or not self.spreadsheet:
            print("✗ Não conectado ao Google Sheets")
            return False
        
        self._sync_in_progress = True
        
        try:
            worksheets = self.spreadsheet.worksheets()
            self.data_dict = {}
            
            for sheet in worksheets:
                sheet_name = sheet.title
                print(f"📄 Processando aba: {sheet_name}")
                
                # Lê todos os dados da aba
                all_values = sheet.get_all_values()
                
                if not all_values or len(all_values) < 2:
                    continue
                
                # Primeira linha são headers
                headers = all_values[0]
                
                # Processa cada linha
                sheet_data = {}
                for row_idx, row in enumerate(all_values[1:], 1):
                    row_dict = {}
                    for col_idx, header in enumerate(headers):
                        if col_idx < len(row):
                            row_dict[header] = row[col_idx]
                        else:
                            row_dict[header] = ""
                    
                    # Usa o primeiro valor como chave (geralmente ID ou nome)
                    key = row[0] if row else f"row_{row_idx}"
                    sheet_data[key] = row_dict
                
                self.data_dict[sheet_name] = sheet_data
            
            self.last_update = time.time()
            self._transformed_data = None  # Limpa cache transformado
            print(f"✓ Dados sincronizados com sucesso! Total de abas: {len(worksheets)}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao sincronizar dados: {e}")
            return False
        finally:
            self._sync_in_progress = False
    
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
    
    def start_auto_sync(self, interval_seconds=300):  # 5 minutos em vez de 60
        """Inicia sincronização automática em background"""
        def auto_sync():
            while True:
                time.sleep(interval_seconds)
                if self.is_connected and not self._sync_in_progress:
                    print(f"🔄 Sincronizando dados ({time.strftime('%H:%M:%S')})")
                    self.sync_data()
        
        thread = Thread(target=auto_sync, daemon=True)
        thread.start()
        print(f"✓ Sincronização automática iniciada (a cada {interval_seconds//60} minutos)")
    
    def get_status(self):
        """Retorna status da conexão"""
        return {
            "connected": self.is_connected,
            "last_update": self.last_update,
            "data_sheets": len(self.data_dict),
            "total_records": sum(len(sheet) for sheet in self.data_dict.values())
        }


# Instância global
sheets_manager = SheetsManager()
