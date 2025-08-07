# RPG Gacha Game

Um jogo RPG Gacha web-based com foco em mobile, desenvolvido com Python (Flask) no backend e HTML/CSS/JS no frontend.

## 🎮 Características

- **Sistema Gacha**: Obtenha personagens com diferentes raridades (1-5 estrelas)
- **Sistema de Batalha por Turnos**: Combate estratégico baseado em velocidade
- **Sistema de Equipes**: Crie equipes com até 4 personagens
- **Sistema de Equipamentos**: Equipe seus personagens para melhorar status
- **Modo História**: Progressão através de capítulos
- **Arena PvP**: Batalhas contra outros jogadores (preparado para multiplayer)
- **Interface SPA**: Navegação fluida sem recarregamento de página
- **Design Mobile-First**: Otimizado para dispositivos móveis

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Flask**: Framework web
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados
- **Flask-CORS**: Para requisições cross-origin

### Frontend
- **HTML5**: Estrutura
- **CSS3**: Estilização com gradientes e animações
- **JavaScript (ES6+)**: Lógica do cliente
- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Ícones

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

1. **Clone o repositório**:
```bash
git clone <url-do-repositorio>
cd gacha_game
```

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**:
   - **Windows**:
   ```bash
   venv\Scripts\activate
   ```
   - **Linux/Mac**:
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

5. **Execute o servidor**:
```bash
python app.py
```

6. **Acesse o jogo**:
Abra seu navegador e vá para `http://localhost:5000`

## 🎯 Como Jogar

### 1. Primeiro Acesso
- O jogo inicia sem personagens
- Vá para a seção "Gacha" para obter seu primeiro personagem
- Cada pull tem chances diferentes baseadas na raridade:
  - 1★: 70%
  - 2★: 20%
  - 3★: 8%
  - 4★: 1.5%
  - 5★: 0.5%

### 2. Gerenciando Personagens
- **Menu de Personagens**: Visualize todos os seus personagens
- **Equipamento**: Clique em "Equipar" para melhorar status
- **Criar Equipe**: Selecione 4 personagens para formar uma equipe

### 3. Sistema de Batalha
- **Ordem de Turnos**: Baseada na velocidade dos personagens
- **Habilidades**: Cada personagem tem habilidades baseadas na raridade
- **Cálculo de Dano**: `Dano = Ataque - Defesa` (mínimo 0)

### 4. Modos de Jogo
- **História**: Progressão através de capítulos
- **Arena PvP**: Batalhas contra outros jogadores (preparado para multiplayer)

## 🏗️ Estrutura do Projeto

```
gacha_game/
├── app.py                 # Servidor Flask principal
├── requirements.txt       # Dependências Python
├── gacha_game.db         # Banco de dados SQLite (criado automaticamente)
├── templates/
│   └── index.html        # Template HTML principal
├── static/
│   ├── style.css         # Estilos CSS
│   └── script.js         # Lógica JavaScript
└── README.md             # Este arquivo
```

## 🔧 API Endpoints

### Personagens
- `GET /api/characters` - Lista todos os personagens disponíveis
- `GET /api/player-characters` - Lista personagens do jogador

### Equipamentos
- `GET /api/equipment` - Lista equipamentos disponíveis

### Equipes
- `GET /api/teams` - Lista equipes do jogador
- `POST /api/teams` - Cria nova equipe

### Batalhas
- `POST /api/battle/start` - Inicia nova batalha
- `POST /api/battle/<id>/action` - Executa ação na batalha

### Gacha
- `POST /api/gacha/pull` - Faz pull no gacha

## 🎨 Sistema de Raridades

### Personagens
- **1★**: Habilidade básica (Ataque Básico)
- **2★**: 2 habilidades ativas + 1 passiva
- **3★**: 3 habilidades ativas + 2 passivas
- **4★**: 4 habilidades ativas + 3 passivas
- **5★**: 5 habilidades ativas + 4 passivas

### Status Base
- **Vida**: HP do personagem
- **Força**: Poder de ataque
- **Defesa**: Redução de dano
- **Velocidade**: Ordem de turnos

## 🔮 Funcionalidades Futuras

- [ ] Sistema de login/registro
- [ ] Multiplayer em tempo real
- [ ] Sistema de ranking
- [ ] Eventos especiais
- [ ] Sistema de guildas
- [ ] Chat em tempo real
- [ ] Sistema de missões diárias
- [ ] Loja de itens
- [ ] Sistema de evolução de personagens

## 🐛 Solução de Problemas

### Erro de Porta em Uso
Se a porta 5000 estiver em uso, modifique a linha no `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Mude para 5001
```

### Erro de Dependências
Se houver problemas com dependências:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Banco de Dados Corrompido
Para resetar o banco de dados:
```bash
rm gacha_game.db
python app.py
```

## 📱 Compatibilidade

- **Navegadores**: Chrome, Firefox, Safari, Edge
- **Dispositivos**: Desktop, Tablet, Mobile
- **Sistemas**: Windows, macOS, Linux

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Entre em contato através do email do desenvolvedor

---

**Desenvolvido com ❤️ para a comunidade de jogos web** 