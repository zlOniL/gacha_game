# 🚀 Setup Rápido - RPG Gacha Game

## Instalação e Execução

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Servidor
```bash
python app.py
```

### 3. Acessar o Jogo
Abra seu navegador e vá para: `http://localhost:5000`

## 🎮 Como Jogar

1. **Primeiro Acesso**: Vá para "Gacha" e faça seu primeiro pull
2. **Gerenciar Personagens**: Use o menu "Personagens" para ver seus personagens
3. **Equipar**: Clique em "Equipar" para melhorar status
4. **Criar Equipe**: Selecione 4 personagens para formar equipe
5. **Batalhar**: Use "História" ou "Arena PvP" para batalhar

## 🔧 Solução de Problemas

### Erro: "No module named 'flask_sqlalchemy'"
```bash
pip install Flask-SQLAlchemy
```

### Erro: Porta 5000 em uso
Modifique a linha no `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Reset do Banco de Dados
```bash
rm gacha_game.db
python app.py
```

## 📱 Funcionalidades

- ✅ Sistema Gacha (1-5 estrelas)
- ✅ Sistema de Batalha por Turnos
- ✅ Sistema de Equipes
- ✅ Sistema de Equipamentos
- ✅ Interface SPA (Single Page Application)
- ✅ Design Mobile-First
- ✅ Modo História
- ✅ Arena PvP (preparado para multiplayer)

## 🎯 Próximos Passos

1. Teste o gacha para obter personagens
2. Crie uma equipe com 4 personagens
3. Teste o sistema de batalha
4. Explore os diferentes modos de jogo

---

**Divirta-se jogando! 🎮** 