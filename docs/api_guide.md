# UNO Game API Guide

## Overview

This guide documents the improved interfaces for the `uno` and `multi` modules, making it easier to develop the game's main body.

## UNO Module - Core Game Logic

### Game Class

The `Game` class manages the entire game state and flow.

#### Key Methods:

```python
# Initialize a game
from uno import Player, Game

players = [Player("Alice"), Player("Bob"), Player("Charlie")]
game = Game(players)

# Get current game state
current_player = game.get_current_player()
top_card = game.get_top_card()

# Play a card
card = current_player.hand[0]
success = game.play_card(current_player, card)

# Advance to next turn
next_player = game.next_turn()

# Check for winner
winner = game.check_winner()
if winner:
    print(f"{winner.name} wins!")
```

### Player Class

The `Player` class represents a player with their hand and score.

#### Key Methods:

```python
player = Player("Alice")

# Draw cards
cards_drawn = player.draw(deck, 2)

# Discard a card
player.discard(deck, card)

# Check if player has a card
has_card = player.has_card(card)

# Get hand value (for scoring)
value = player.get_hand_value()

# Check if hand is empty
is_winner = player.is_empty_hand()
```

### Deck Class

The `Deck` class manages the draw pile and discard pile.

#### Key Methods:

```python
from uno import Deck

deck = Deck()

# Draw cards
cards = deck.draw(5)

# Discard a card
deck.discard(card)

# Get top card of discard pile
top = deck.get_top_discard()

# Check if deck is empty
empty = deck.is_empty()
```

### Rules Class

The `Rules` class contains all game rule logic.

#### Key Methods:

```python
from uno import Rules

# Check if a card can be played
can_play = Rules.is_valid_play(card, game)

# Check if player can play any card
can_play_any = Rules.is_able_to_play(player, game)

# Get all playable cards for a player
playable_cards = Rules.get_playable_cards(player, game)

# Apply special card effects
Rules.apply_special_effects(card, game)

# Check for winner
is_winner = Rules.is_winner(player)

# Calculate score
total_score = Rules.score(game)

# Check draw four challenge
challenge_success = Rules.can_challenge_draw_four(challenger, challenged_player, previous_color)
```

## Multi Module - Multiplayer Networking

### Action Enum

Standardized action types for game communication:

```python
from multi import Action

# Available actions:
Action.JOIN_ROOM
Action.LEAVE_ROOM
Action.START_GAME
Action.END_GAME
Action.PLAY_CARD
Action.DRAW_CARD
Action.CHALLENGE_DRAW_FOUR
Action.CHOOSE_COLOR
Action.SAY_UNO
Action.SYNC_GAME_STATE
Action.SYNC_HAND
Action.SYNC_TOP_CARD
Action.SYNC_TURN
Action.INVALID_ACTION
Action.ERROR
```

### Message Utilities

Helper functions for creating standardized messages:

```python
from multi.utils import create_action_message, create_error_message, create_state_sync_message
from multi import Action

# Create an action message
msg = create_action_message(Action.PLAY_CARD, {
    'player': 'Alice',
    'card': {'color': 'red', 'sort': 'number', 'value': 5}
})

# Create an error message
error_msg = create_error_message("Invalid move", "Card cannot be played on current top card")

# Create a state sync message
state_msg = create_state_sync_message({
    'turn': 0,
    'draw': 2,
    'reverse': False,
    'top_card': {'color': 'blue', 'sort': 'draw_two', 'value': 20}
})
```

### Host Class

The host manages the game server and all client connections.

#### Key Methods:

```python
from multi import Host

# Create a host
host = Host("HostPlayer", "My Room", 1234)

# Send message to specific connection
host.send(connection, message)

# Broadcast to all clients
host.broadcast(message, exclude="PlayerName")

# Process received actions
host.process_action(action_data)

# Run the host loop
host.run()
```

### Client Class

The client connects to a host and participates in the game.

#### Key Methods:

```python
from multi import Client, Action

# Create a client
client = Client("ClientPlayer")

# Join a room
client.join(("192.168.1.100", 50001), password=1234)

# Send an action to the host
client.send_action(Action.PLAY_CARD, {
    'card': {'color': 'red', 'sort': 'number', 'value': 5}
})

# Run the client loop
client.run()
```

### Room Class

The `Room` class manages room discovery via multicast.

#### Key Methods:

```python
from multi import Room

# Create a room
room = Room("My Room", 1234, 50001)

# Broadcast room availability
room.broadcast()

# Receive available rooms (class method)
Room.recv()

# Access discovered rooms
for (ip, port), room_info in Room.rooms.items():
    print(f"Room: {room_info.name} at {ip}:{port}")
```

## Game Development Flow

### Basic Single Player Game Loop

```python
from uno import Player, Game, Rules

# Setup
players = [Player("Alice"), Player("Bob")]
game = Game(players)

# Game loop
while True:
    current_player = game.get_current_player()
    top_card = game.get_top_card()
    
    # Get playable cards
    playable = Rules.get_playable_cards(current_player, game)
    
    if playable:
        # Player chooses a card
        chosen_card = playable[0]  # Example: choose first playable
        game.play_card(current_player, chosen_card)
    else:
        # Player must draw
        current_player.draw(game.deck, 1)
    
    # Check for winner
    if game.check_winner():
        print(f"{current_player.name} wins!")
        break
    
    # Next turn
    game.next_turn()
```

### Basic Multiplayer Host Setup

```python
from multi import Host, Action
from uno import Player, Game

host = Host("Host", "Game Room", 1234)

# Wait for players to join...
# When ready to start:
host.room.status = multi.ROOM_ONGOING

# Create game with all players
players = [Player(name) for name in host.room.players]
game = Game(players)

# Game loop
while True:
    # Process actions from clients
    for action in host.actions:
        if action['type'] == Action.PLAY_CARD.value:
            # Handle play card action
            pass
        elif action['type'] == Action.DRAW_CARD.value:
            # Handle draw card action
            pass
    
    # Sync game state to all clients
    state = {
        'turn': game.turn,
        'top_card': game.get_top_card().__dict__,
        'draw': game.draw
    }
    host.broadcast(create_state_sync_message(state))
```

## Best Practices

1. **Type Safety**: Use type hints consistently. All interfaces now have proper type annotations.

2. **Error Handling**: Use the provided exception classes (`SocketClosedMessage`, `GameStartedMessage`, `GameEndedMessage`) for flow control.

3. **Message Format**: Always use the message creation utilities (`create_action_message`, etc.) for consistency.

4. **State Synchronization**: Keep game state on the host and sync to clients regularly using standardized messages.

5. **Action Processing**: Use the `Action` enum for all game actions to ensure consistency.

6. **Validation**: Always validate game actions using `Rules` methods before applying them.

## Summary of Improvements

### UNO Module
- Added comprehensive type hints
- Added helper methods for common operations
- Improved documentation
- Better state management in Game class
- Added validation and query methods

### Multi Module
- Introduced Action enum for standardized communication
- Added message creation utilities
- Improved type hints and documentation
- Added broadcast functionality to Host
- Added send_action method to Client
- Better error handling patterns

These improvements provide a solid foundation for developing the game's main body while maintaining clean separation between game logic (uno) and networking (multi).
