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
        this.apiBase = '/wuglarst';
        this.init();
    }

    async init() {
        console.log("🌟 Wuglarst инициализация v3.0...");
        this.bindEvents();
        console.log("✅ Обработчики событий привязаны");
        this.connectWebSocket();
        await this.loadStatus();
    }

    bindEvents() {
        const demoBtn = document.getElementById('demoBtn');
        if (demoBtn) {
            demoBtn.addEventListener('click', () => this.loadDemo());
        }
        
        const futabaBtn = document.getElementById('futabaProfileBtn');
        if (futabaBtn) {
            futabaBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.openFutabaProfile();
            });
        }
        
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadStatus());
        }
        
        const clearEvents = document.getElementById('clearEvents');
        if (clearEvents) {
            clearEvents.addEventListener('click', () => this.clearEvents());
        }
    }

    connectWebSocket() {
        this.ws = new WebSocket('/wuglarst/ws');
        this.ws.onopen = () => {
            this.updateConnectionStatus('connected');
        };
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        this.ws.onclose = () => {
            setTimeout(() => this.connectWebSocket(), 3000);
        };
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
            this.showNotification("🌱 Девочки проснулись!");
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
        document.querySelectorAll('.scientist-avatar').forEach(el => el.classList.remove('selected'));
        
        for (const [name, sci] of Object.entries(this.scientists)) {
            const avatar = document.createElement('div');
            avatar.className = 'scientist-avatar';
            avatar.dataset.name = name;
            avatar.style.left = `${sci.position.x}px`;
            avatar.style.top = `${sci.position.y}px`;
            avatar.innerHTML = `${sci.avatar}<div class="status-ring status-${sci.status}"></div>`;
            avatar.addEventListener('click', () => this.selectScientist(name));
            avatar.title = `${sci.name}: ${sci.current_task || 'Без задачи'}`;
            mapGrid.appendChild(avatar);
        }
    }

    selectScientist(name) {
        this.selectedScientist = name;
        const sci = this.scientists[name];
        if (!sci) return;
        document.querySelectorAll('.scientist-avatar').forEach(el => el.classList.toggle('selected', el.dataset.name === name));
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
        const statusMap = { 'working': '💼 Работает', 'thinking': '🤔 Думает', 'idle': '⏸️ Ожидание', 'error': '❌ Ошибка' };
        return statusMap[status] || status;
    }

    renderPersonalityBars(personality) {
        if (!personality || Object.keys(personality).length === 0) return '';
        const bars = [
            { key: 'empathy', label: 'Эмпатия' },
            { key: 'cynicism', label: 'Цинизм' },
            { key: 'logic', label: 'Логика' },
            { key: 'creativity', label: 'Креативность' }
        ];
        return `<div class="personality-bars">${bars.map(bar => {
            const value = personality[bar.key] || 0;
            return `<div class="personality-bar"><span class="bar-label">${bar.label}</span><div class="bar-track"><div class="bar-fill ${bar.key}" style="width: ${value * 100}%"></div></div><span class="bar-value">${value.toFixed(2)}</span></div>`;
        }).join('')}</div>`;
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
        if (countEl) countEl.textContent = `${Object.keys(this.scientists).length} ученых`;
    }

    showNotification(message) {
        const notif = document.createElement('div');
        notif.style.cssText = `position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #00d4ff, #9b59b6); color: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 4px 20px rgba(0, 212, 255, 0.4); z-index: 1000; animation: slideIn 0.3s ease-out;`;
        notif.textContent = message;
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), 3000);
    }

    // ===== ПРОФИЛЬ ФУТАБЫ =====

    async openFutabaProfile() {
        const modal = document.getElementById('futabaProfileModal');
        const content = document.getElementById('futabaProfileContent');
        if (!modal || !content) return;
        
        modal.style.display = 'block';
        content.innerHTML = '<div class="loading">⚖️ Загрузка профиля Футабы...</div>';
        
        try {
            const [profileRes, resultsRes] = await Promise.all([
                fetch(`${this.apiBase}/api/futaba/profile`),
                fetch(`${this.apiBase}/api/futaba/results`)
            ]);
            const profileData = await profileRes.json();
            const resultsData = await resultsRes.json();
            
            if (profileData.status === 'ok' && profileData.profile) {
                content.innerHTML = this.renderFutabaProfile(profileData.profile, resultsData);
                setTimeout(() => {
                    const workBtn = document.getElementById('workTabBtn');
                    if (workBtn) workBtn.addEventListener('click', () => this.openFutabaWork());
                }, 100);
            } else {
                content.innerHTML = '<div class="loading">❌ Ошибка загрузки профиля</div>';
            }
        } catch (error) {
            console.error('Ошибка загрузки профиля Футабы:', error);
            content.innerHTML = '<div class="loading">❌ Ошибка подключения к серверу</div>';
        }
    }

    closeFutabaProfile() {
        const modal = document.getElementById('futabaProfileModal');
        if (modal) modal.style.display = 'none';
    }

    async openFutabaWork() {
        const modal = document.getElementById('futabaProfileModal');
        const content = document.getElementById('futabaProfileContent');
        if (!modal || !content) return;
        
        modal.style.display = 'block';
        content.innerHTML = '<div class="loading">📝 Загрузка документов Футабы...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/futaba/documents`);
            const data = await response.json();
            
            if (data.status === 'ok' && data.documents.length > 0) {
                content.innerHTML = this.renderWorkTabs(data.documents);
                setTimeout(() => {
                    this.bindTabs();
                    const backBtn = document.querySelector('.back-btn');
                    if (backBtn) backBtn.addEventListener('click', () => this.closeFutabaProfile());
                }, 100);
            } else {
                content.innerHTML = '<div class="loading">❌ Документы не найдены</div>';
            }
        } catch (error) {
            console.error('Ошибка загрузки документов:', error);
            content.innerHTML = '<div class="loading">❌ Ошибка подключения к серверу</div>';
        }
    }

    bindTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(btn.dataset.tab)?.classList.add('active');
            });
        });
    }

    renderWorkTabs(documents) {
        const tabButtonsHTML = documents.map((doc, i) =>
            `<button class="tab-btn ${i === 0 ? 'active' : ''}" data-tab="tab-${i}">${doc.name}</button>`
        ).join('');
        
        const tabContentsHTML = documents.map((doc, i) =>
            `<div class="tab-content ${i === 0 ? 'active' : ''}" id="tab-${i}">
                <div class="doc-header"><h3>${doc.name}</h3><p class="doc-path">${doc.path}</p></div>
                <div class="doc-content">${this.renderMarkdown(doc.content)}</div>
            </div>`
        ).join('');
        
        return `
            <div class="work-header">
                <button class="back-btn" style="background:none;border:none;color:var(--accent-blue);cursor:pointer;font-size:1rem;padding:0;margin-bottom:1rem;">← Назад к профилю</button>
                <h2>📝 Работа Футабы</h2>
                <p class="work-subtitle">Документы: конституция, законы, кодексы, протоколы</p>
            </div>
            <div class="tabs-container">
                <div class="tab-buttons">${tabButtonsHTML}</div>
                <div class="tab-panels">${tabContentsHTML}</div>
            </div>
        `;
    }

    renderMarkdown(text) {
        return text
            .replace(/^### (.+)$/gm, '<h4>$1</h4>')
            .replace(/^## (.+)$/gm, '<h3>$1</h3>')
            .replace(/^# (.+)$/gm, '<h2>$1</h2>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code>$1</code>')
            .replace(/^---$/gm, '<hr>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
            .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }

    renderFutabaProfile(profile, workResults = null) {
        let resultsHTML = '';
        if (workResults && workResults.summary) {
            const s = workResults.summary;
            resultsHTML = `
                <div class="profile-section">
                    <div class="profile-section-title">📊 Результаты работы</div>
                    <div class="profile-section-content">
                        <div class="profile-grid">
                            <div class="profile-card"><div class="profile-card-title">Версия ядра</div><div class="profile-card-value" style="color:var(--accent-green);">${s.version || '—'}</div></div>
                            <div class="profile-card"><div class="profile-card-title">Циклов выполнено</div><div class="profile-card-value">${s.cycles || 0}</div></div>
                            <div class="profile-card"><div class="profile-card-title">Изменений применено</div><div class="profile-card-value">${s.changes_applied || 0}</div></div>
                            <div class="profile-card"><div class="profile-card-title">Самопроверок пройдено</div><div class="profile-card-value" style="color:var(--accent-green);">${s.self_checks_passed || 0}</div></div>
                        </div>
                        <div style="margin-top:1.5rem;">
                            <div class="profile-section-title" style="font-size:1.1rem;">📚 Правовые исследования</div>
                            <div class="profile-grid">
                                <div class="profile-card"><div class="profile-card-title">Тем изучено</div><div class="profile-card-value">${s.legal_topics_studied || 0}</div></div>
                                <div class="profile-card"><div class="profile-card-title">Законов изучено</div><div class="profile-card-value">${s.laws_studied || 0}</div></div>
                                <div class="profile-card"><div class="profile-card-title">Субъектов права</div><div class="profile-card-value">${s.entities_documented || 0}</div></div>
                                <div class="profile-card"><div class="profile-card-title">Страниц в кэше</div><div class="profile-card-value">${s.web_pages_cached || 0}</div></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="profile-header">
                <span class="profile-avatar-large">${profile.avatar}</span>
                <div class="profile-name">${profile.name}</div>
                <div class="profile-name-jp">${profile.name_jp} — ${profile.meaning}</div>
                <div class="profile-badge">${profile.status}</div>
            </div>
            
            <div class="profile-section">
                <div class="profile-section-title">📊 Данные</div>
                <div class="profile-section-content">
                    <div class="profile-grid">
                        <div class="profile-card"><div class="profile-card-title">Роль</div><div class="profile-card-value">${profile.data.hierarchy.position}</div></div>
                        <div class="profile-card"><div class="profile-card-title">Миссия</div><div class="profile-card-value">${profile.data.mission}</div></div>
                        <div class="profile-card"><div class="profile-card-title">Версия</div><div class="profile-card-value">${profile.version}</div></div>
                        <div class="profile-card"><div class="profile-card-title">Подчиняется</div><div class="profile-card-value">${profile.data.hierarchy.reporting_to}</div></div>
                    </div>
                    <div style="margin-top:1.5rem;">
                        <div class="profile-section-title" style="font-size:1.1rem;">👥 Подчинённые</div>
                        <ul class="profile-list">${profile.data.hierarchy.subordinates.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                    <div style="margin-top:1.5rem;">
                        <div class="profile-section-title" style="font-size:1.1rem;">🎯 Уровни полномочий</div>
                        <ul class="profile-list">${Object.entries(profile.data.authority_levels).map(([level, desc]) => `<li><strong>${level}:</strong> ${desc}</li>`).join('')}</ul>
                    </div>
                    <div style="margin-top:1.5rem;">
                        <div class="profile-section-title" style="font-size:1.1rem;">📚 Уровни знаний</div>
                        <ul class="profile-list">${Object.entries(profile.data.knowledge_levels).map(([level, desc]) => `<li><strong>${level}:</strong> ${desc}</li>`).join('')}</ul>
                    </div>
                </div>
            </div>
            
            <div class="profile-section">
                <div class="profile-section-title">⚙️ Ядро системы</div>
                <div class="profile-section-content">
                    <p style="margin-bottom:1rem;color:var(--text-secondary);">${profile.core.description}</p>
                    <div class="profile-section-title" style="font-size:1.1rem;">🔧 Модули ядра</div>
                    <ul class="profile-list">${profile.core.modules.map(mod => `<li><strong>${mod.name}</strong> — ${mod.function}<br><small style="color:var(--text-secondary);">📄 ${mod.file}</small></li>`).join('')}</ul>
                    <div style="margin-top:1.5rem;">
                        <div class="profile-section-title" style="font-size:1.1rem;">🔄 Автономный цикл</div>
                        <ul class="profile-list">${profile.core.autonomous_cycle.map(step => `<li>${step}</li>`).join('')}</ul>
                    </div>
                </div>
            </div>
            
            ${resultsHTML}
            
            <div class="profile-section">
                <div class="profile-section-title">⚖️ Правовая деятельность</div>
                <div class="profile-section-content">
                    <p style="margin-bottom:1rem;color:var(--text-secondary);">${profile.legal_activity.description}</p>
                    <div class="profile-section-title" style="font-size:1.1rem;">📖 Отрасли права</div>
                    <ul class="profile-list">${profile.legal_activity.studied_areas.map(a => `<li>${a}</li>`).join('')}</ul>
                    <div style="margin-top:1.5rem;">
                        <div class="profile-section-title" style="font-size:1.1rem;">📜 Документы</div>
                        <ul class="profile-list">${profile.legal_activity.legal_documents_created.map(d => `<li>${d}</li>`).join('')}</ul>
                    </div>
                    <div style="margin-top:1.5rem;">
                        <div class="profile-section-title" style="font-size:1.1rem;">📋 Конституция</div>
                        <ul class="profile-list">${profile.legal_activity.constitution.key_principles.map(p => `<li>${p}</li>`).join('')}</ul>
                    </div>
                    <div style="margin-top:1rem;">
                        <div class="profile-card-title">Абсолютные запреты:</div>
                        <ul class="profile-list">${profile.legal_activity.constitution.fundamental_prohibitions.map(p => `<li>❌ ${p}</li>`).join('')}</ul>
                    </div>
                </div>
            </div>
            
            <div class="profile-quote">
                "${profile.quote}"
                <span class="profile-quote-author">— Футаба</span>
            </div>
            
            <div style="margin-top:1.5rem;text-align:center;">
                <button id="workTabBtn" class="btn btn-futaba" style="padding:1rem 2rem;font-size:1.1rem;border-radius:12px;">
                    📝 Работа Футабы — Документы
                </button>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new WuglarstApp();
});

document.addEventListener('click', (event) => {
    if (event.target.closest('.close-btn')) window.app.closeFutabaProfile();
});

document.addEventListener('click', (event) => {
    const modal = document.getElementById('futabaProfileModal');
    if (event.target === modal) window.app.closeFutabaProfile();
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') window.app.closeFutabaProfile();
});
