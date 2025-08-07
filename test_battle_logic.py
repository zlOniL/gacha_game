#!/usr/bin/env python3
"""
Script de teste para verificar a lógica de ordem de ação
"""

def test_battle_order():
    """Testa a lógica de ordem de ação"""
    
    # Simular uma batalha
    battle = {
        'action_order': [
            {'name': 'Player1', 'type': 'player', 'speed': 15, 'status': {'is_alive': True, 'is_conscious': True}, 'has_acted_this_turn': False},
            {'name': 'Enemy1', 'type': 'enemy', 'speed': 12, 'status': {'is_alive': True, 'is_conscious': True}, 'has_acted_this_turn': False},
            {'name': 'Player2', 'type': 'player', 'speed': 10, 'status': {'is_alive': True, 'is_conscious': True}, 'has_acted_this_turn': False},
            {'name': 'Enemy2', 'type': 'enemy', 'speed': 8, 'status': {'is_alive': True, 'is_conscious': True}, 'has_acted_this_turn': False}
        ],
        'turn_idx': 0,
        'current_round': 1
    }
    
    def get_next_actor(battle):
        """Obtém o próximo ator válido na ordem de ação"""
        order = battle['action_order']
        current_idx = battle['turn_idx']
        
        # Procurar próximo ator vivo e consciente que ainda não agiu neste round
        for i in range(len(order)):
            idx = (current_idx + i) % len(order)
            combatant = order[idx]
            
            if (combatant['status']['is_alive'] and 
                combatant['status']['is_conscious'] and 
                not combatant['has_acted_this_turn']):
                return idx
        
        return None

    def advance_turn(battle):
        """Avança para o próximo turno"""
        order = battle['action_order']
        current_idx = battle['turn_idx']
        
        # Marcar que o ator atual já agiu
        if current_idx < len(order):
            order[current_idx]['has_acted_this_turn'] = True
            print(f"{order[current_idx]['name']} agiu")
        
        # Verificar se todos agiram neste round
        alive_combatants = [c for c in order if c['status']['is_alive'] and c['status']['is_conscious']]
        all_acted = all(c['has_acted_this_turn'] for c in alive_combatants)
        
        if all_acted and len(alive_combatants) > 0:
            # Novo round - resetar flags
            battle['current_round'] += 1
            for c in order:
                c['has_acted_this_turn'] = False
            print(f"Novo round iniciado: {battle['current_round']}")
        
        # Próximo ator
        next_idx = get_next_actor(battle)
        if next_idx is not None:
            battle['turn_idx'] = next_idx
            print(f"Próximo ator: {order[next_idx]['name']} (índice {next_idx})")
        else:
            # Ninguém pode agir - batalha acabou
            battle['status'] = 'finished'
            print("Ninguém pode agir - batalha finalizada")
    
    print("=== Teste de Ordem de Ação ===")
    print("Ordem inicial (por velocidade):")
    for i, combatant in enumerate(battle['action_order']):
        print(f"{i}: {combatant['name']} (velocidade: {combatant['speed']})")
    
    print("\n=== Simulando turnos ===")
    
    # Simular alguns turnos
    for turn in range(8):
        current = battle['action_order'][battle['turn_idx']]
        print(f"\nTurno {turn + 1}: {current['name']} (Round {battle['current_round']})")
        
        # Simular ação
        advance_turn(battle)
        
        if battle.get('status') == 'finished':
            break

if __name__ == "__main__":
    test_battle_order() 