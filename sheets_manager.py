import gspread
from google.oauth2.service_account import Credentials
import os
import json
import time
import re

# Só carrega .env localmente (não existe na Vercel)
if not os.getenv('VERCEL'):
    from dotenv import load_dotenv
    load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

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

    def _get_credentials(self):
        """
        Obtém credenciais do Google.
        - Em produção (Vercel): lê da variável GOOGLE_CREDENTIALS_JSON
        - Em desenvolvimento local: lê do arquivo credentials.json
        """
        # 1. Tenta variável de ambiente (Vercel / produção)
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            try:
                creds_dict = json.loads(credentials_json)
                print("✓ Usando credenciais da variável de ambiente")
                return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            except json.JSONDecodeError as e:
                raise ValueError(f"GOOGLE_CREDENTIALS_JSON inválido: {e}")

        # 2. Fallback: arquivo local (apenas desenvolvimento)
        creds_file = os.getenv('SHEETS_CREDENTIALS_FILE', 'credentials.json')
        if os.path.exists(creds_file):
            print(f"✓ Usando arquivo de credenciais local: {creds_file}")
            return Credentials.from_service_account_file(creds_file, scopes=SCOPES)

        return None

    def _initialize_connection(self):
        """Inicializa a conexão com Google Sheets"""
        try:
            sheets_url = os.getenv('GOOGLE_SHEETS_URL')

            if not sheets_url:
                print("⚠ GOOGLE_SHEETS_URL não configurada - usando modo demo")
                self._load_demo_data()
                return

            creds = self._get_credentials()

            if not creds:
                print("⚠ Credenciais não encontradas - usando modo demo")
                self._load_demo_data()
                return

            client = gspread.authorize(creds)
            sheet_id = self._extract_sheet_id(sheets_url)
            self.spreadsheet = client.open_by_key(sheet_id)
            self.is_connected = True
            print("✓ Conectado ao Google Sheets!")
            self.sync_data()

        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            print("📊 Usando modo demo")
            self._load_demo_data()

    def _extract_sheet_id(self, url):
        """Extrai o ID da planilha da URL"""
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"URL de planilha inválida: {url}")

    def _load_demo_data(self):
        """Carrega dados de demonstração"""
        print("📊 Carregando dados de demonstração...")
        self.is_connected = False
        self.data_dict = {
            'Resumo_Por_Turma': {
                'DEMO_1A_Q1': {
                    'AvaliacaoID': 'DEMO_LP_5ANO', 'TurmaID': '5A', 'QuestaoID': 'Q_1',
                    '%Acerto': '75%', 'TotalRespostas': '20', 'TotalAcertos': '15',
                    'Habilidade': 'EF05LP10', 'Descritor': 'Reconhecer o efeito de humor em textos'
                },
                'DEMO_1A_Q2': {
                    'AvaliacaoID': 'DEMO_LP_5ANO', 'TurmaID': '5A', 'QuestaoID': 'Q_2',
                    '%Acerto': '60%', 'TotalRespostas': '20', 'TotalAcertos': '12',
                    'Habilidade': 'EF35LP06', 'Descritor': 'Recuperar o sentido do texto'
                },
                'DEMO_1B_Q1': {
                    'AvaliacaoID': 'DEMO_LP_5ANO', 'TurmaID': '5B', 'QuestaoID': 'Q_1',
                    '%Acerto': '85%', 'TotalRespostas': '20', 'TotalAcertos': '17',
                    'Habilidade': 'EF05LP10', 'Descritor': 'Reconhecer o efeito de humor em textos'
                },
                'DEMO_1B_Q2': {
                    'AvaliacaoID': 'DEMO_LP_5ANO', 'TurmaID': '5B', 'QuestaoID': 'Q_2',
                    '%Acerto': '70%', 'TotalRespostas': '20', 'TotalAcertos': '14',
                    'Habilidade': 'EF35LP06', 'Descritor': 'Recuperar o sentido do texto'
                }
            }
        }
        self.last_update = time.time()
        self._transformed_data = None
        print("✓ Dados de demonstração carregados!")

    def sync_data(self):
        """Sincroniza dados da planilha"""
        if not self.is_connected:
            return True

        if self._sync_in_progress:
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
                    row_dict = {
                        header: (row[col_idx] if col_idx < len(row) else "")
                        for col_idx, header in enumerate(headers)
                    }
                    key = row[0] if row else f"row_{row_idx}"
                    sheet_data[key] = row_dict

                self.data_dict[sheet_name] = sheet_data

            self.last_update = time.time()
            self._transformed_data = None
            print(f"✓ Sincronizados {len(worksheets)} abas!")
            return True

        except Exception as e:
            print(f"✗ Erro ao sincronizar: {e}")
            return False
        finally:
            self._sync_in_progress = False

    def get_sheet_data(self, sheet_name):
        return self.data_dict.get(sheet_name, {})

    def get_all_data(self):
        if self._transformed_data is None:
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

            transformed.setdefault(avaliacao_id, {})
            transformed[avaliacao_id].setdefault(turma_id, {})

            try:
                pct = float(row_data.get('%Acerto', '0').replace('%', ''))
                total = int(row_data.get('TotalRespostas', '0'))
                acertos = int(row_data.get('TotalAcertos', '0'))
            except (ValueError, TypeError):
                pct, total, acertos = 0.0, 0, 0

            transformed[avaliacao_id][turma_id][questao_id] = {
                'pct': pct,
                'total': total,
                'acertos': acertos,
                'habilidade': row_data.get('Habilidade', ''),
                'descritor': row_data.get('Descritor', '')
            }

        return transformed

    def start_auto_sync(self, interval_seconds=300):
        pass  # Desativado na Vercel (serverless não suporta threads persistentes)

    def get_status(self):
        return {
            "connected": self.is_connected,
            "last_update": self.last_update,
            "data_sheets": len(self.data_dict),
            "total_records": sum(len(s) for s in self.data_dict.values()),
            "mode": "demo" if not self.is_connected else "live"
        }   

# Instância global
sheets_manager = SheetsManager()