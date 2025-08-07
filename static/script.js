// Variáveis globais
let currentScreen = 'main-menu';
let playerCharacters = [];
let allCharacters = [];
let equipment = [];
let teams = [];
let currentBattle = null;
let selectedCharacter = null;
let teamSlots = [null, null, null, null];

// API Base URL
const API_BASE = '';

// Função para navegar entre telas
function showScreen(screenId) {
    // Esconder todas as telas
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Mostrar a tela selecionada
    document.getElementById(screenId).classList.add('active');
    currentScreen = screenId;
    
    // Carregar dados específicos da tela
    switch(screenId) {
        case 'characters':
            loadPlayerCharacters();
            break;
        case 'equipment':
            if (selectedCharacter) {
                loadEquipmentScreen();
            }
            break;
        case 'team-creation':
            loadTeamCreation();
            break;
        case 'battle':
            if (currentBattle) {
                loadBattleScreen();
            }
            break;
    }
}

// Função para carregar personagens do jogador
async function loadPlayerCharacters() {
    try {
        const response = await fetch(`${API_BASE}/api/player-characters`);
        playerCharacters = await response.json();
        
        const charactersList = document.getElementById('characters-list');
        charactersList.innerHTML = '';
        
        playerCharacters.forEach(character => {
            const characterCard = createCharacterCard(character, true);
            charactersList.appendChild(characterCard);
        });
        
        if (playerCharacters.length === 0) {
            charactersList.innerHTML = `
                <div class="col-12 text-center">
                    <p>Você ainda não tem personagens. Faça um pull no Gacha!</p>
                    <button class="btn btn-primary" onclick="showScreen('gacha')">
                        Ir para Gacha
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar personagens:', error);
    }
}

// Função para criar card de personagem
function createCharacterCard(character, isPlayerCharacter = false) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-3';
    
    const rarityClass = `rarity-${character.rarity}`;
    const rarityStars = '★'.repeat(character.rarity);
    
    col.innerHTML = `
        <div class="character-card ${rarityClass}" onclick="selectCharacter(${character.id})">
            <div class="character-avatar">
                <img src="${character.image_url || '/static/char_1.png'}" alt="${character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
            </div>
            <h5 class="text-center">${character.name}</h5>
            <div class="text-center text-warning mb-2">${rarityStars}</div>
            <div class="status-bar">
                <span class="status-label">HP:</span>
                <span class="status-value">${character.hp}</span>
            </div>
            <div class="status-bar">
                <span class="status-label">Ataque:</span>
                <span class="status-value">${character.attack}</span>
            </div>
            <div class="status-bar">
                <span class="status-label">Defesa:</span>
                <span class="status-value">${character.defense}</span>
            </div>
            <div class="status-bar">
                <span class="status-label">Velocidade:</span>
                <span class="status-value">${character.speed}</span>
            </div>
            ${isPlayerCharacter ? `
                <div class="mt-2">
                    <button class="btn btn-sm btn-success me-1" onclick="event.stopPropagation(); showEquipment(${character.id})">
                        <i class="fas fa-sword"></i> Equipar
                    </button>
                </div>
            ` : ''}
        </div>
    `;
    
    return col;
}

// Função para selecionar personagem
function selectCharacter(characterId) {
    selectedCharacter = playerCharacters.find(c => c.id === characterId);
    if (selectedCharacter) {
        showScreen('equipment');
    }
}

// Função para mostrar tela de equipamento
function showEquipment(characterId) {
    selectedCharacter = playerCharacters.find(c => c.id === characterId);
    showScreen('equipment');
}

// Função para carregar tela de equipamento
async function loadEquipmentScreen() {
    if (!selectedCharacter) return;
    
    // Carregar equipamentos
    try {
        const response = await fetch(`${API_BASE}/api/equipment`);
        equipment = await response.json();
        
        // Mostrar informações do personagem
        const characterInfo = document.getElementById('selected-character-info');
        characterInfo.innerHTML = `
            <h6>${selectedCharacter.name}</h6>
            <div class="status-bar">
                <span class="status-label">HP:</span>
                <span class="status-value">${selectedCharacter.hp}</span>
            </div>
            <div class="status-bar">
                <span class="status-label">Ataque:</span>
                <span class="status-value">${selectedCharacter.attack}</span>
            </div>
            <div class="status-bar">
                <span class="status-label">Defesa:</span>
                <span class="status-value">${selectedCharacter.defense}</span>
            </div>
            <div class="status-bar">
                <span class="status-label">Velocidade:</span>
                <span class="status-value">${selectedCharacter.speed}</span>
            </div>
        `;
        
        // Mostrar equipamentos
        const equipmentList = document.getElementById('equipment-list');
        equipmentList.innerHTML = '';
        
        equipment.forEach(item => {
            const equipmentDiv = document.createElement('div');
            equipmentDiv.className = 'equipment-item';
            equipmentDiv.innerHTML = `
                <h6>${item.name}</h6>
                <small class="text-muted">Tipo: ${item.type}</small>
                ${item.hp_bonus > 0 ? `<div>HP: +${item.hp_bonus}</div>` : ''}
                ${item.attack_bonus > 0 ? `<div>Ataque: +${item.attack_bonus}</div>` : ''}
                ${item.defense_bonus > 0 ? `<div>Defesa: +${item.defense_bonus}</div>` : ''}
                ${item.speed_bonus > 0 ? `<div>Velocidade: +${item.speed_bonus}</div>` : ''}
            `;
            equipmentDiv.onclick = () => equipItem(item);
            equipmentList.appendChild(equipmentDiv);
        });
    } catch (error) {
        console.error('Erro ao carregar equipamentos:', error);
    }
}

// Função para equipar item
function equipItem(item) {
    // Aqui você implementaria a lógica para equipar o item
    alert(`Equipando ${item.name} em ${selectedCharacter.name}`);
}

// Função para adicionar personagem à equipe
function addToTeam(characterId) {
    selectedCharacter = playerCharacters.find(c => c.id === characterId);
    showScreen('team-creation');
}

// Função para carregar tela de criação de equipe
function loadTeamCreation() {
    const availableCharacters = document.getElementById('available-characters');
    availableCharacters.innerHTML = '';
    
    playerCharacters.forEach(character => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-3 mb-3';
        col.innerHTML = `
            <div class="character-card" onclick="addCharacterToSlot(${character.id})">
                <div class="character-avatar">
                    <img src="${character.image_url || '/static/char_1.png'}" alt="${character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
                </div>
                <h6 class="text-center">${character.name}</h6>
                <div class="text-center text-warning">${'★'.repeat(character.rarity)}</div>
            </div>
        `;
        availableCharacters.appendChild(col);
    });
}

// Função para adicionar personagem ao slot
function addCharacterToSlot(characterId) {
    const emptySlot = teamSlots.findIndex(slot => slot === null);
    if (emptySlot !== -1) {
        teamSlots[emptySlot] = characterId;
        updateTeamSlots();
    }
}

// Função para atualizar slots da equipe
function updateTeamSlots() {
    const slots = document.querySelectorAll('.team-slot');
    slots.forEach((slot, index) => {
        const characterId = teamSlots[index];
        if (characterId) {
            const character = playerCharacters.find(c => c.id === characterId);
            slot.innerHTML = `
                <div class="character-avatar">
                    <img src="${character.image_url || '/static/char_1.png'}" alt="${character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
                </div>
                <h6>${character.name}</h6>
                <button class="btn btn-sm btn-danger" onclick="removeFromSlot(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            slot.classList.add('filled');
        } else {
            slot.innerHTML = `
                <div class="slot-placeholder">
                    <i class="fas fa-plus"></i>
                    <p>Slot ${index + 1}</p>
                </div>
            `;
            slot.classList.remove('filled');
        }
    });
}

// Função para remover personagem do slot
function removeFromSlot(slotIndex) {
    teamSlots[slotIndex] = null;
    updateTeamSlots();
}

// Função para salvar equipe
async function saveTeam() {
    const filledSlots = teamSlots.filter(slot => slot !== null);
    if (filledSlots.length < 4) {
        alert('Você precisa selecionar 4 personagens para criar uma equipe!');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/teams`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: 'Equipe Principal',
                character1_id: teamSlots[0],
                character2_id: teamSlots[1],
                character3_id: teamSlots[2],
                character4_id: teamSlots[3],
                is_main_team: true
            })
        });
        
        const result = await response.json();
        alert('Equipe salva com sucesso!');
        showScreen('characters');
    } catch (error) {
        console.error('Erro ao salvar equipe:', error);
        alert('Erro ao salvar equipe');
    }
}

// Função para iniciar batalha
async function startBattle(battleType, phase = 1) {
    try {
        const response = await fetch(`${API_BASE}/api/battle/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: battleType,
                phase: phase
            })
        });
        
        currentBattle = await response.json();
        showScreen('battle');
    } catch (error) {
        console.error('Erro ao iniciar batalha:', error);
        alert('Erro ao iniciar batalha');
    }
}

// Função para carregar tela de batalha
function loadBattleScreen() {
    if (!currentBattle) return;
    
    // Renderizar inimigos
    const enemiesContainer = document.getElementById('enemies');
    enemiesContainer.innerHTML = '';
    
    currentBattle.enemies.forEach((enemy, index) => {
        const enemyDiv = document.createElement('div');
        enemyDiv.className = 'col-md-6 mb-3';
        const hpPercent = (enemy.status.current_hp / enemy.max_hp) * 100;
        const isDead = !enemy.status.is_alive;
        
        enemyDiv.innerHTML = `
            <div class="battle-character enemy ${isDead ? 'dead' : ''}">
                <img src="${enemy.image_url || '/static/enemy_1.png'}" alt="${enemy.name}" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 10px; ${isDead ? 'opacity: 0.5;' : ''}">
                <h6>${enemy.name}</h6>
                <div class="health-bar">
                    <div class="health-fill ${hpPercent < 30 ? 'low' : ''}" style="width: ${hpPercent}%"></div>
                </div>
                <div class="status-bar">
                    <span>HP: ${enemy.status.current_hp}/${enemy.max_hp}</span>
                    <span>Ataque: ${enemy.attack}</span>
                </div>
                ${isDead ? '<div class="text-danger"><small>Morto</small></div>' : ''}
            </div>
        `;
        enemiesContainer.appendChild(enemyDiv);
    });
    
    // Renderizar equipe do jogador
    const playerTeamContainer = document.getElementById('player-team');
    playerTeamContainer.innerHTML = '';
    
    currentBattle.player_team.forEach(character => {
        const characterDiv = document.createElement('div');
        characterDiv.className = 'col-md-6 mb-3';
        const hpPercent = (character.status.current_hp / character.max_hp) * 100;
        const isDead = !character.status.is_alive;
        
        characterDiv.innerHTML = `
            <div class="battle-character player ${isDead ? 'dead' : ''}">
                <img src="${character.image_url || '/static/char_1.png'}" alt="${character.name}" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 10px; ${isDead ? 'opacity: 0.5;' : ''}">
                <h6>${character.name}</h6>
                <div class="health-bar">
                    <div class="health-fill ${hpPercent < 30 ? 'low' : ''}" style="width: ${hpPercent}%"></div>
                </div>
                <div class="status-bar">
                    <span>HP: ${character.status.current_hp}/${character.max_hp}</span>
                    <span>Ataque: ${character.attack}</span>
                </div>
                ${isDead ? '<div class="text-danger"><small>Morto</small></div>' : ''}
            </div>
        `;
        playerTeamContainer.appendChild(characterDiv);
    });
    
    // Renderizar ordem de ação
    renderActionOrder();
    
    // Carregar ações de batalha
    loadBattleActions();
}

// Função para renderizar ordem de ação
function renderActionOrder() {
    const actionOrderContainer = document.getElementById('action-order');
    if (!actionOrderContainer) {
        // Criar container se não existir
        const battleField = document.querySelector('.battle-field');
        const orderDiv = document.createElement('div');
        orderDiv.id = 'action-order';
        orderDiv.className = 'action-order-container mb-3';
        orderDiv.innerHTML = '<h6>Ordem de Ação:</h6><div class="action-order-list"></div>';
        battleField.insertBefore(orderDiv, battleField.firstChild);
    }
    
    const orderList = document.querySelector('.action-order-list');
    orderList.innerHTML = '';
    
    // Adicionar informação do round
    const roundInfo = document.createElement('div');
    roundInfo.className = 'round-info mb-2';
    roundInfo.innerHTML = `<strong>Round: ${currentBattle.current_round || 1}</strong>`;
    orderList.appendChild(roundInfo);
    
    if (currentBattle.action_order) {
        currentBattle.action_order.forEach((combatant, index) => {
            const orderItem = document.createElement('div');
            const isCurrent = index === currentBattle.turn_idx;
            const isDead = !combatant.status.is_alive;
            const hasActed = combatant.has_acted_this_turn;
            
            orderItem.className = `action-order-item ${combatant.type === 'player' ? 'player' : 'enemy'} ${isCurrent ? 'current' : ''} ${isDead ? 'dead' : ''} ${hasActed ? 'acted' : ''}`;
            orderItem.innerHTML = `
                <img src="${combatant.image_url || (combatant.type === 'player' ? '/static/char_1.png' : '/static/enemy_1.png')}" 
                     alt="${combatant.name}" 
                     style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; ${isDead ? 'opacity: 0.5;' : ''}">
                ${isDead ? '<div class="dead-indicator">💀</div>' : ''}
                ${hasActed ? '<div class="acted-indicator">✓</div>' : ''}
            `;
            orderList.appendChild(orderItem);
        });
    }
}

// Função para carregar ações de batalha
function loadBattleActions() {
    const actionsContainer = document.getElementById('battle-actions');
    if (!currentBattle || !currentBattle.action_order) return;
    
    const currentActor = currentBattle.action_order[currentBattle.turn_idx];
    if (!currentActor || currentActor.type !== 'player' || !currentActor.status.is_alive) {
        actionsContainer.innerHTML = '<p>Aguardando ação do inimigo...</p>';
        // Auto-executar ação do inimigo após 1 segundo
        setTimeout(() => performEnemyAction(), 1000);
        return;
    }
    
    // Verificar se já agiu neste round
    if (currentActor.has_acted_this_turn) {
        actionsContainer.innerHTML = '<p>Aguardando próximo turno...</p>';
        // Auto-avançar turno após 1 segundo
        setTimeout(() => performEnemyAction(), 1000);
        return;
    }
    
    actionsContainer.innerHTML = `
        <h6>Turno de: ${currentActor.name}</h6>
        <p><small>Round: ${currentBattle.current_round || 1}</small></p>
        <button class="battle-action" onclick="performAction('Ataque Básico')">
            <i class="fas fa-sword"></i> Ataque Básico
        </button>
        ${currentActor.skills && currentActor.skills.includes('Ataque Especial') ? `
            <button class="battle-action" onclick="performAction('Ataque Especial')">
                <i class="fas fa-magic"></i> Ataque Especial
            </button>
        ` : ''}
        ${currentActor.skills && currentActor.skills.includes('Cura') ? `
            <button class="battle-action" onclick="performAction('Cura')">
                <i class="fas fa-heart"></i> Cura
            </button>
        ` : ''}
        <div class="mt-3">
            <h6>Selecione um alvo:</h6>
            <div id="target-selection"></div>
        </div>
    `;
    
    // Renderizar alvos disponíveis
    renderTargets();
}

// Função para renderizar alvos
function renderTargets() {
    const targetSelection = document.getElementById('target-selection');
    targetSelection.innerHTML = '';
    
    const currentActor = currentBattle.action_order[currentBattle.turn_idx];
    if (!currentActor || currentActor.type !== 'player') return;
    
    // Determinar tipo de alvo baseado na ação selecionada
    const selectedAction = window.selectedAction || 'Ataque Básico';
    
    if (selectedAction === 'Cura') {
        // Alvos aliados vivos
        currentBattle.player_team.forEach(ally => {
            if (ally.status.is_alive) {
                const targetBtn = document.createElement('button');
                targetBtn.className = 'btn btn-outline-success btn-sm me-2 mb-2';
                targetBtn.innerHTML = `
                    <img src="${ally.image_url || '/static/char_1.png'}" style="width: 20px; height: 20px; border-radius: 50%; margin-right: 5px;">
                    ${ally.name} (HP: ${ally.status.current_hp})
                `;
                targetBtn.onclick = () => selectTarget(ally.id, 'Cura');
                targetSelection.appendChild(targetBtn);
            }
        });
    } else {
        // Alvos inimigos vivos
        currentBattle.enemies.forEach(enemy => {
            if (enemy.status.is_alive) {
                const targetBtn = document.createElement('button');
                targetBtn.className = 'btn btn-outline-danger btn-sm me-2 mb-2';
                targetBtn.innerHTML = `
                    <img src="${enemy.image_url || '/static/enemy_1.png'}" style="width: 20px; height: 20px; border-radius: 50%; margin-right: 5px;">
                    ${enemy.name} (HP: ${enemy.status.current_hp})
                `;
                targetBtn.onclick = () => selectTarget(enemy.id, selectedAction);
                targetSelection.appendChild(targetBtn);
            }
        });
    }
}

// Função para selecionar ação
function performAction(action) {
    window.selectedAction = action;
    renderTargets();
}

// Função para selecionar alvo
function selectTarget(targetId, action) {
    const currentActor = currentBattle.action_order[currentBattle.turn_idx];
    if (!currentActor || currentActor.type !== 'player') return;
    
    executeAction(action, targetId);
}

// Função para executar ação de batalha
async function executeAction(action, targetId) {
    try {
        const response = await fetch(`${API_BASE}/api/battle/${currentBattle.battle_id}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: action,
                target_id: targetId
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'finished') {
            if (result.winner === 'player') {
                showVictoryScreen();
            } else {
                alert('Derrota!');
                endBattle();
            }
        } else {
            // Atualizar estado da batalha
            currentBattle.action_order = result.action_order;
            currentBattle.turn_idx = result.turn_idx;
            currentBattle.status = result.status;
            currentBattle.current_round = result.current_round;
            
            // Atualizar HP dos personagens
            if (result.action_order) {
                result.action_order.forEach(combatant => {
                    if (combatant.type === 'player') {
                        const playerChar = currentBattle.player_team.find(p => p.id === combatant.id);
                        if (playerChar) {
                            playerChar.status = combatant.status;
                        }
                    } else {
                        const enemy = currentBattle.enemies.find(e => e.id === combatant.id);
                        if (enemy) {
                            enemy.status = combatant.status;
                        }
                    }
                });
            }
            
            // Recarregar tela de batalha
            loadBattleScreen();
        }
        
        console.log(result.message);
    } catch (error) {
        console.error('Erro ao executar ação:', error);
    }
}

// Função para executar ação do inimigo automaticamente
async function performEnemyAction() {
    try {
        const response = await fetch(`${API_BASE}/api/battle/${currentBattle.battle_id}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        if (result.status === 'finished') {
            if (result.winner === 'player') {
                showVictoryScreen();
            } else {
                alert('Derrota!');
                endBattle();
            }
        } else {
            // Atualizar estado da batalha
            currentBattle.action_order = result.action_order;
            currentBattle.turn_idx = result.turn_idx;
            currentBattle.status = result.status;
            currentBattle.current_round = result.current_round;
            
            // Atualizar HP dos personagens
            if (result.action_order) {
                result.action_order.forEach(combatant => {
                    if (combatant.type === 'player') {
                        const playerChar = currentBattle.player_team.find(p => p.id === combatant.id);
                        if (playerChar) {
                            playerChar.status = combatant.status;
                        }
                    } else {
                        const enemy = currentBattle.enemies.find(e => e.id === combatant.id);
                        if (enemy) {
                            enemy.status = combatant.status;
                        }
                    }
                });
            }
            
            // Recarregar tela de batalha
            loadBattleScreen();
        }
    } catch (error) {
        console.error('Erro ao executar ação do inimigo:', error);
    }
}

// Função para mostrar tela de vitória
function showVictoryScreen() {
    const battleContainer = document.querySelector('.battle-field');
    battleContainer.innerHTML = `
        <div class="victory-screen text-center">
            <h2 class="text-success">🎉 Vitória! 🎉</h2>
            <p>Parabéns! Você derrotou todos os inimigos!</p>
            <div class="mt-3">
                <button class="btn btn-success me-2" onclick="nextPhase()">Próxima Fase</button>
                <button class="btn btn-primary" onclick="showScreen('story')">Voltar ao Menu</button>
            </div>
        </div>
    `;
}

// Função para próxima fase
function nextPhase() {
    // Implementar lógica para próxima fase
    alert('Próxima fase em desenvolvimento!');
    showScreen('story');
}

// Função para finalizar batalha
function endBattle() {
    currentBattle = null;
    showScreen('main-menu');
}

// Função para fazer pull no gacha
async function pullGacha() {
    try {
        const response = await fetch(`${API_BASE}/api/gacha/pull`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.character) {
            const resultContainer = document.getElementById('gacha-result');
            const rarityStars = '★'.repeat(result.character.rarity);
            
            resultContainer.innerHTML = `
                <div class="gacha-result">
                    <h4>🎉 Parabéns! 🎉</h4>
                    <div class="gacha-character rarity-${result.character.rarity}">
                        <div class="character-avatar">
                            <img src="${result.character.image_url || '/static/char_1.png'}" alt="${result.character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
                        </div>
                        <h5>${result.character.name}</h5>
                        <div class="text-warning">${rarityStars}</div>
                        <p>${result.message}</p>
                    </div>
                </div>
            `;
            
            // Recarregar personagens do jogador
            await loadPlayerCharacters();
        } else {
            alert('Erro no gacha: ' + result.error);
        }
    } catch (error) {
        console.error('Erro no gacha:', error);
        alert('Erro ao fazer pull no gacha');
    }
}

// Inicialização quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados iniciais
    loadPlayerCharacters();
    
    // Adicionar listeners para navegação
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-screen]')) {
            showScreen(e.target.dataset.screen);
        }
    });
});

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover após 3 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
} 