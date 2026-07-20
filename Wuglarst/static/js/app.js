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
        // Wuglarst смонтирован по /wuglarst, все пути абсолютные
        this.apiBase = '/wuglarst';
        
        this.init();
    }

    async init() {
        console.log("🌟 Wuglarst инициализация v2.0...");
        
        // Привязка событий
        this.bindEvents();
        console.log("✅ Обработчики событий привязаны");
        
        // Подключение WebSocket
        this.connectWebSocket();
        
        // Загрузка начальных данных
        await this.loadStatus();
    }

    bindEvents() {
        // Кнопка демо-данных
        const demoBtn = document.getElementById('demoBtn');
        if (demoBtn) {
            demoBtn.addEventListener('click', () => this.loadDemo());
            console.log('✅ Кнопка демо привязана');
        } else {
            console.warn('⚠️ Кнопка demoBtn не найдена');
        }
        
        // Кнопка профиля Футабы
        const futabaBtn = document.getElementById('futabaProfileBtn');
        if (futabaBtn) {
            futabaBtn.addEventListener('click', (e) => {
                console.log('🔥🔥🔥 КЛИК ПО КНОПКЕ ФУТАБЫ! 🔥🔥🔥');
                console.log('🔥 Текущий URL:', window.location.href);
                console.log('🔥 apiBase:', this.apiBase);
                console.log('🔥 Модальное окно:', document.getElementById('futabaProfileModal'));
                e.preventDefault();
                e.stopPropagation();
                this.openFutabaProfile();
            });
            console.log('✅ Кнопка профиля Футабы привязана успешно!');
        } else {
            console.error('❌❌❌ Кнопка futabaProfileBtn НЕ НАЙДЕНА! ❌❌❌');
            console.error('❌ Доступные кнопки:', Array.from(document.querySelectorAll('button')).map(b => b.id).join(', '));
        }
        
        // Кнопка обновления
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadStatus());
        }
        
        // Кнопка очистки событий
        const clearEvents = document.getElementById('clearEvents');
        if (clearEvents) {
            clearEvents.addEventListener('click', () => this.clearEvents());
        }
    }

    connectWebSocket() {
        // Wuglarst смонтирован по /wuglarst
        this.ws = new WebSocket('/wuglarst/ws');
        
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
            this.showNotification("🌱 Девочки проснулись! Они начнут жить сами через 15 секунд...");
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

    async openFutabaProfile() {
        console.log('🔍 Открываю профиль Футабы...');
        const modal = document.getElementById('futabaProfileModal');
        const content = document.getElementById('futabaProfileContent');
        
        if (!modal || !content) {
            console.error('❌ Модальное окно не найдено');
            return;
        }
        
        // Показываем модальное окно
        modal.style.display = 'block';
        content.innerHTML = '<div class="loading">⚖️ Загрузка профиля Футабы...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/futaba/profile`);
            const data = await response.json();
            
            if (data.status === 'ok' && data.profile) {
                content.innerHTML = this.renderFutabaProfile(data.profile);
                console.log('✅ Профиль Футабы загружен');
            } else {
                content.innerHTML = '<div class="loading">❌ Ошибка загрузки профиля</div>';
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки профиля Футабы:', error);
            content.innerHTML = '<div class="loading">❌ Ошибка подключения к серверу</div>';
        }
    }

    closeFutabaProfile() {
        const modal = document.getElementById('futabaProfileModal');
        if (modal) {
            modal.style.display = 'none';
            console.log('🔒 Профиль Футабы закрыт');
        }
    }

    renderFutabaProfile(profile) {
        return `
            <!-- Шапка профиля -->
            <div class="profile-header">
                <span class="profile-avatar-large">${profile.avatar}</span>
                <div class="profile-name">${profile.name}</div>
                <div class="profile-name-jp">${profile.name_jp} — ${profile.meaning}</div>
                <div class="profile-badge">${profile.status}</div>
            </div>
            
            <!-- Основные данные -->
            <div class="profile-section">
                <div class="profile-section-title">📊 Данные</div>
                <div class="profile-section-content">
                    <div class="profile-grid">
                        <div class="profile-card">
                            <div class="profile-card-title">Роль</div>
                            <div class="profile-card-value">${profile.data.hierarchy.position}</div>
                        </div>
                        <div class="profile-card">
                            <div class="profile-card-title">Миссия</div>
                            <div class="profile-card-value">${profile.data.mission}</div>
                        </div>
                        <div class="profile-card">
                            <div class="profile-card-title">Версия системы</div>
                            <div class="profile-card-value">${profile.version}</div>
                        </div>
                        <div class="profile-card">
                            <div class="profile-card-title">Подчиняется</div>
                            <div class="profile-card-value">${profile.data.hierarchy.reporting_to}</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">👥 Подчинённые девочки-учёные</div>
                        <ul class="profile-list">
                            ${profile.data.hierarchy.subordinates.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">🎯 Уровни полномочий</div>
                        <ul class="profile-list">
                            ${Object.entries(profile.data.authority_levels).map(([level, desc]) => 
                                `<li><strong>${level}:</strong> ${desc}</li>`
                            ).join('')}
                        </ul>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">📚 Уровни знаний</div>
                        <ul class="profile-list">
                            ${Object.entries(profile.data.knowledge_levels).map(([level, desc]) => 
                                `<li><strong>${level}:</strong> ${desc}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Ядро системы -->
            <div class="profile-section">
                <div class="profile-section-title">⚙️ Ядро системы</div>
                <div class="profile-section-content">
                    <p style="margin-bottom: 1rem; color: var(--text-secondary);">${profile.core.description}</p>
                    
                    <div class="profile-section-title" style="font-size: 1.1rem;">🔧 Модули ядра</div>
                    <ul class="profile-list">
                        ${profile.core.modules.map(mod => 
                            `<li><strong>${mod.name}</strong> — ${mod.function}<br><small style="color: var(--text-secondary);">📄 ${mod.file}</small></li>`
                        ).join('')}
                    </ul>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">🔄 Автономный цикл работы</div>
                        <ul class="profile-list">
                            ${profile.core.autonomous_cycle.map(step => `<li>${step}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Правовая деятельность -->
            <div class="profile-section">
                <div class="profile-section-title">⚖️ Правовая деятельность</div>
                <div class="profile-section-content">
                    <p style="margin-bottom: 1rem; color: var(--text-secondary);">${profile.legal_activity.description}</p>
                    
                    <div class="profile-section-title" style="font-size: 1.1rem;">📖 Изучаемые отрасли права</div>
                    <ul class="profile-list">
                        ${profile.legal_activity.studied_areas.map(area => `<li>${area}</li>`).join('')}
                    </ul>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">📜 Создаваемые правовые документы</div>
                        <ul class="profile-list">
                            ${profile.legal_activity.legal_documents_created.map(doc => `<li>${doc}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">🏛️ Изучаемые субъекты права</div>
                        <ul class="profile-list">
                            ${profile.legal_activity.legal_entities_studies.map(entity => `<li>${entity}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">📋 Конституция (v2.0.0)</div>
                        <div class="profile-grid">
                            <div class="profile-card">
                                <div class="profile-card-title">Статус</div>
                                <div class="profile-card-value" style="color: var(--accent-green);">✅ ${profile.legal_activity.constitution.status}</div>
                            </div>
                            <div class="profile-card">
                                <div class="profile-card-title">Статей</div>
                                <div class="profile-card-value">${profile.legal_activity.constitution.articles}</div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 1rem;">
                            <div class="profile-card-title">Фундаментальные принципы:</div>
                            <ul class="profile-list">
                                ${profile.legal_activity.constitution.key_principles.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                        
                        <div style="margin-top: 1rem;">
                            <div class="profile-card-title">Абсолютные запреты:</div>
                            <ul class="profile-list">
                                ${profile.legal_activity.constitution.fundamental_prohibitions.map(p => `<li>❌ ${p}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">📚 Правовые документы</div>
                        <ul class="profile-list">
                            <li>📜 Законы (основные): ${profile.legal_activity.laws.core_laws}</li>
                            <li>⚖️ Законы (субъекты права): ${profile.legal_activity.laws.legal_entities_laws}</li>
                            <li>📋 Кодекс этики: ${profile.legal_activity.ethics_code.file}</li>
                        </ul>
                    </div>
                    
                    <div style="margin-top: 1.5rem;">
                        <div class="profile-section-title" style="font-size: 1.1rem;">🔄 Протоколы</div>
                        <ul class="profile-list">
                            ${profile.legal_activity.protocols.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Цитата -->
            <div class="profile-quote">
                "${profile.quote}"
                <span class="profile-quote-author">— Футаба</span>
            </div>
        `;
    }
}

// Запуск приложения при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WuglarstApp();
});

// =====================================================================
//  ОБРАБОТЧИКИ МОДАЛЬНОГО ОКНА ФУТАБЫ
// =====================================================================

// Закрытие по клику на крестик
document.addEventListener('click', (event) => {
    if (event.target.closest('.close-btn')) {
        window.app.closeFutabaProfile();
    }
});

// Закрытие при клике вне модального окна
document.addEventListener('click', (event) => {
    const modal = document.getElementById('futabaProfileModal');
    if (event.target === modal) {
        window.app.closeFutabaProfile();
    }
});

// Закрытие по Escape
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        window.app.closeFutabaProfile();
    }
});
