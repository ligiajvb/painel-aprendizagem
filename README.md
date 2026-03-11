# 📊 Painel de Aprendizagem — Integração com Google Sheets

Sistema de visualização de dados diagnósticos com integração em **tempo real** com Google Sheets.

## ✨ Características

- ✓ **Tempo Real**: Sincroniza dados a cada 30 segundos
- ✓ **Google Sheets API**: Sem necessidade de exportar manualmente
- ✓ **Em Memória**: Dados armazenados em `dict` para acesso rápido
- ✓ **Responsivo**: Dashboard completo com gráficos e tabelas
- ✓ **Escalável**: Pronto para migração para banco de dados

## 📁 Estrutura do Projeto

```
painel-aprendizagem/
├── app.py                    # Aplicação Flask principal
├── sheets_manager.py         # Gerenciador de integração com Sheets
├── requirements.txt          # Dependências Python
├── .env                      # Variáveis de ambiente
├── credentials.json          # Credenciais do Google (GERADO)
├── SHEETS_CONFIG.md          # Guia de configuração
├── README.md                 # Este arquivo
├── template/
│   └── index.html            # HTML principal
└── static/
    └── css/
        └── index.css         # Estilos CSS (separado do HTML)
```

## 🚀 Quick Start

### 1. Instalar Dependências

```bash
cd painel-aprendizagem
pip install -r requirements.txt
```

### 2. Configurar Google Sheets (veja `SHEETS_CONFIG.md`)

1. Criar projeto no Google Cloud
2. Ativar Google Sheets API
3. Criar conta de serviço e baixar JSON
4. Renomear para `credentials.json`
5. Compartilhar planilha com o email da conta

### 3. Configurar `.env`

```env
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/SEU_ID/edit
SHEETS_CREDENTIALS_FILE=credentials.json
```

### 4. Iniciar Aplicação

```bash
python app.py
```

Acesse: **http://localhost:5000**

## 📊 Estrutura de Dados

Seus dados no Sheets devem estar organizados assim:

**Aba: DIAG_2026_LP_5ANO**

| Avaliacao | Turma | Q_1  | Q_2 | ... |
|-----------|-------|------|-----|-----|
| 2026      | 5C    | 50.0 | 75  | ... |
| 2026      | 5B    | 100  | 80  | ... |

Os dados são carregados automaticamente e convertidos para o formato do dashboard.

## 🔄 Sincronização Automática

- ✓ Sincroniza ao iniciar a aplicação
- ✓ Sincroniza a cada **30 segundos** em background
- ✓ Sincroniza ao clicar no botão "🔄 Sincronizar"

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Página principal |
| GET | `/api/data` | Todos os dados |
| GET | `/api/sheet/<nome>` | Dados de uma aba |
| GET | `/api/status` | Status de conexão |
| POST | `/api/sync` | Sincronizar manualmente |

### Exemplo de Uso

```javascript
// Obter todos os dados
fetch('/api/data')
  .then(r => r.json())
  .then(data => console.log(data));

// Sincronizar manualmente
fetch('/api/sync', { method: 'POST' })
  .then(r => r.json())
  .then(status => console.log(status));
```

## 🔍 Status de Conexão

Acesse **http://localhost:5000/api/status** para ver:

```json
{
  "connected": true,
  "last_update": 1678900000,
  "data_sheets": 8,
  "total_records": 450,
  "timestamp": "2026-03-10T14:30:00"
}
```

## 🛠️ Arquitetura

### `app.py` (Flask)
- Renderiza HTML
- Oferece endpoints REST
- Gerencia sincronização

### `sheets_manager.py` (Inteligência)
- Conecta ao Google Sheets API
- Sincroniza dados periodicamente
- Armazena em `dict` em memória
- Oferece métodos de acesso aos dados

### `index.html` (Frontend)
- Consome API
- Sincroniza dados em tempo real
- Exibe gráficos com Chart.js
- Responsivo e interativo

## 📈 Próximos Passos

1. **Testar com seus dados**: Configure a planilha e veja os dados em tempo real
2. **Customizar intervalo**: Altere `interval_seconds` em `sheets_manager.start_auto_sync()`
3. **Adicionar mais abas**: Crie novas abas no Sheets e veja na aplicação
4. **Migrar para DB**: Quando estável, adicione SQLite, PostgreSQL, etc.

### Migração para Banco de Dados (Futuro)

```python
# Em sheets_manager.py
def save_to_database(self):
    for sheet_name, data in self.data_dict.items():
        # Salvar em banco de dados
        pass
```

## 🐛 Troubleshooting

**P: Dados não aparecem?**
- Verifique se `credentials.json` existe
- Confirme se a planilha foi compartilhada
- Veja os logs no console

**P: Sincronização muito lenta?**
- Altere `interval_seconds` em `app.py`
- Reduza de 30 para 10 segundos

**P: Erro de autenticação?**
- Regenere `credentials.json`
- Verifique email da conta de serviço

## 📝 Log de Atualizações

### v1.0 (Atual)
- ✓ Integração com Google Sheets API
- ✓ Sincronização automática
- ✓ Dashboard responsivo
- ✓ Endpoints REST
- ✓ Botão de sincronização manual

### v1.1 (Próximo)
- Suporte a múltiplas planilhas
- Cache local
- Banco de dados
- Autenticação de usuários

## 📞 Suporte

Para problemas, consulte `SHEETS_CONFIG.md` ou verifique os logs da aplicação.

---

**Desenvolvido com ❤️**  
Painel de Aprendizagem — Sistema Diagnóstico 2026