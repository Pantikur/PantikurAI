# Протокол 6: Протокол Сетевого Кода

## Назначение
Отвечает за многопользовательские режимы, синхронизацию данных и сетевую архитектуру.

## Компоненты

### 1. Сетевая архитектура
- **Client-Server:** Authoritative server model
- **Peer-to-Peer:** Опциональная P2P для голосового чата
- **Reliable UDP:** KCP/ENet транспорт
- **Connection Management:** Лобби, сессии, matchmaking

### 2. Репликация состояния
- **RPC (Remote Procedure Call):** Вызов функций на другом конце
- **State Synchronization:** Пакетная отправка состояния объектов
- **Interest Management:** Hierarchy, spatial partitioning
- **Dirty Flag System:** Отправка только изменённых данных

### 3. Синхронизация
- **Client-side Prediction:** Предсказание действий клиента
- **Lag Compensation:** Компенсация задержки для стрельбы
- **Interpolation:** Плавное отображение удалённых объектов
- **Snapshot Interpolation:** Buffer-based interpolation

### 4. Matchmaking
- **Rank-based:** Подбор по рейтингу (ELO, MMR)
- **Region-based:** Подбор по географическому региону
- **Skill-based:** Подбор по уровню мастерства
- **Custom Lobbies:** Создание пользовательских лобби

### 5. Безопасность
- **Encryption:** TLS/DTLS для всех соединений
- **Anti-cheat:** Серверная валидация действий
- **Serialization:** Safe binary protocols (MessagePack, FlatBuffers)
- **Rate Limiting:** Ограничение частоты сообщений

## API
```python
# Инициализация сетевого модуля
sidney.engine.network.init(server_port=7777, max_clients=64, encryption=True)

# Серверная часть
server = sidney.engine.network.create_server(max_clients=64)
server.on_client_connect(handle_client_connect)
server.on_client_disconnect(handle_client_disconnect)
server.start()

# Клиентская часть
client = sidney.engine.network.create_client()
client.connect("192.168.1.100", 7777)

# Репликация объектов
replicated_entity = sidney.engine.network.create_replicated_entity(
    type="player",
    sync_position=True,
    sync_rotation=True,
    sync_animation=True
)

# RPC вызовы
client.rpc("shoot", target_pos=(10, 2, 5), damage=25)
server.broadcast("player_joined", player_id=new_player.id)

# Matchmaking
match = sidney.engine.network.matchmaking.find_match(
    rank_range=(1000, 1500),
    region="EU",
    max_latency=100
)

# Состояние соединения
status = sidney.engine.network.get_connection_status()
latency = sidney.engine.network.get_latency()
packet_loss = sidney.engine.network.get_packet_loss()

# Шаг сети
sidney.engine.network.step(dt=1/60)
```

## Оптимизация
- Delta compression (отправка только изменений)
- Message batching (группировка пакетов)
- QoS приоритизация (critical > game > chat)
- Connection recovery (reconnect без потери состояния)

## Статус: Инициализирован ✓
