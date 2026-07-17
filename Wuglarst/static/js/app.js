/**
 * Wuglarst — Визуальное пространство ИИ-ученых
 * JavaScript для управления интерфейсом
 */

class WuglarstApp {
    constructor() {
        this.ws = null;
        this.selectedScientist = null;
        this.scientists = {};
        this.events = [];
        // Используем относительный путь — работает и на /, и на /wuglarst
        this.apiBase = '';
        
        this.init();
    }

    async init() {
        console.log("🌟 Wuglarst инициализация...");
        
        // Привязка событий
        this.bindEvents();
        
        // Подключение WebSocket
        this.connectWebSocket();
        
        // Загрузка начальных данных
        await this.loadStatus();
    }

    bindEvents() {
        // Кнопка демо-данных
        document.getElementById('demoBtn')?.addEventListener('click', () => this.loadDemo());
        
        // Кнопка обновления
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.loadStatus());
        
        // Кнопка очистки событий
        document.getElementById('clearEvents')?.addEventListener('click', () => this.clearEvents());
    }

    connectWebSocket() {
        // Относительный путь — работает через прокси Timeweb
        this.ws = new WebSocket(`/ws`);
        
        this.ws.onopen = () => {
            console.log("✅ WebSocket подключен");
            this.updateConnectionStatus('connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log("🔌 WebSocket отключен, переподключение через 3с...");
            this.updateConnectionStatus('disconnected');
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error("❌ WebSocket ошибка:", error);
            this.updateConnectionStatus('disconnected');
        };
    }

    updateConnectionStatus(status) {
        const indicator = document.getElementById('connectionStatus');
        if (!indicator) return;
        
        const dot = indicator.querySelector('.status-dot');
        const text = indicator.querySelector('span:last-child');
        
        indicator.className = 'status-indicator';
        
        if (status === 'connected') {
            dot.classList.add('connected');
            text.textContent = 'Подключено';
        } else if (status === 'disconnected') {
            dot.classList.add('disconnected');
            text.textContent = 'Отключено';
        } else {
            text.textContent = 'Подключение...';
        }
    }

    handleWebSocketMessage(data) {
        if (data.type === 'scientist_update' || data.type === 'system_update') {
            this.updateSystem(data.data);
        } else if (data.type === 'event_update') {
            this.updateEvents(data.data.events);
        }
    }

    async loadStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            const data = await response.json();
            this.updateSystem(data);
        } catch (error) {
            console.error("Ошибка загрузки статуса:", error);
        }
    }

    async loadDemo() {
        try {
            const response = await fetch(`${this.apiBase}/api/demo/populate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            console.log("✅ Демо-данные загружены:", data);
            
            // Показываем уведомление
            this.showNotification("🎮 Демо-данные загружены!");
        } catch (error) {
            console.error("Ошибка загрузки демо:", error);
        }
    }

    updateSystem(data) {
        if (data.scientists) {
            this.scientists = data.scientists;
            this.renderMap();
            this.updateScientistCount();
        }
        
        if (data.events) {
            this.events = data.events;
            this.renderEvents();
        }
    }

    updateEvents(events) {
        this.events = events;
        this.renderEvents();
    }

    renderMap() {
        const mapGrid = document.getElementById('mapGrid');
        if (!mapGrid) return;
        
        mapGrid.innerHTML = '';
        
        // Очистка выбранных
        document.querySelectorAll('.scientist-avatar').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Создание аватаров
        for (const [name, sci] of Object.entries(this.scientists)) {
            const avatar = document.createElement('div');
            avatar.className = 'scientist-avatar';
            avatar.dataset.name = name;
            avatar.style.left = `${sci.position.x}px`;
            avatar.style.top = `${sci.position.y}px`;
            
            avatar.innerHTML = `
                ${sci.avatar}
                <div class="status-ring status-${sci.status}"></div>
            `;
            
            // Клик по аватару
            avatar.addEventListener('click', () => this.selectScientist(name));
            
            // Тултип
            avatar.title = `${sci.name}: ${sci.current_task || 'Без задачи'}`;
            
            mapGrid.appendChild(avatar);
        }
    }

    selectScientist(name) {
        this.selectedScientist = name;
        const sci = this.scientists[name];
        if (!sci) return;
        
        // Выделение аватара
        document.querySelectorAll('.scientist-avatar').forEach(el => {
            el.classList.toggle('selected', el.dataset.name === name);
        });
        
        // Обновление карточки
        this.renderScientistCard(sci);
    }

    renderScientistCard(sci) {
        const card = document.getElementById('scientistCard');
        if (!card) return;
        
        card.innerHTML = `
            <div class="scientist-info">
                <div class="scientist-header">
                    <div class="scientist-avatar-large">${sci.avatar}</div>
                    <div>
                        <div class="scientist-name">${sci.name}</div>
                        <div class="scientist-status">${this.getStatusText(sci.status)}</div>
                    </div>
                </div>
                
                <div class="task-info">
                    <div class="task-label">Текущая задача:</div>
                    <div class="task-value">${sci.current_task || 'Нет задачи'}</div>
                </div>
                
                ${this.renderPersonalityBars(sci.personality)}
                
                <div class="last-activity">
                    <div class="task-label">Последняя активность:</div>
                    <div class="task-value">${new Date(sci.last_activity).toLocaleString('ru-RU')}</div>
                </div>
            </div>
        `;
    }

    getStatusText(status) {
        const statusMap = {
            'working': '💼 Работает',
            'thinking': '🤔 Думает',
            'idle': '⏸️ Ожидание',
            'error': '❌ Ошибка'
        };
        return statusMap[status] || status;
    }

    renderPersonalityBars(personality) {
        if (!personality || Object.keys(personality).length === 0) {
            return '';
        }
        
        const bars = [
            { key: 'empathy', label: 'Эмпатия' },
            { key: 'cynicism', label: 'Цинизм' },
            { key: 'logic', label: 'Логика' },
            { key: 'creativity', label: 'Креативность' }
        ];
        
        return `
            <div class="personality-bars">
                ${bars.map(bar => {
                    const value = personality[bar.key] || 0;
                    return `
                        <div class="personality-bar">
                            <span class="bar-label">${bar.label}</span>
                            <div class="bar-track">
                                <div class="bar-fill ${bar.key}" style="width: ${value * 100}%"></div>
                            </div>
                            <span class="bar-value">${value.toFixed(2)}</span>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    renderEvents() {
        const list = document.getElementById('eventsList');
        if (!list) return;
        
        if (this.events.length === 0) {
            list.innerHTML = '<div class="no-events"><p>Пока нет событий</p></div>';
            return;
        }
        
        list.innerHTML = this.events.map(event => `
            <div class="event-item">
                <div class="event-time">${new Date(event.timestamp).toLocaleString('ru-RU')}</div>
                <div class="event-message">${event.event}</div>
            </div>
        `).join('');
    }

    clearEvents() {
        this.events = [];
        this.renderEvents();
    }

    updateScientistCount() {
        const countEl = document.getElementById('scientistCount');
        if (countEl) {
            const count = Object.keys(this.scientists).length;
            countEl.textContent = `${count} ученых`;
        }
    }

    showNotification(message) {
        // Простое уведомление
        const notif = document.createElement('div');
        notif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #00d4ff, #9b59b6);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.4);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notif.textContent = message;
        document.body.appendChild(notif);
        
        setTimeout(() => {
            notif.remove();
        }, 3000);
    }
}

// Запуск приложения при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WuglarstApp();
});
