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
        
        const createStateBtn = document.getElementById('createStateBtn');
        if (createStateBtn) {
            createStateBtn.addEventListener('click', () => this.openCreateState());
        }
        
        const nobukaBtn = document.getElementById('nobukaEditorBtn');
        if (nobukaBtn) {
            nobukaBtn.addEventListener('click', () => this.openNobukaEditor());
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

    async openCreateState() {
        const modal = document.getElementById('createStateModal');
        const content = document.getElementById('createStateContent');
        if (!modal || !content) return;
        
        modal.style.display = 'block';
        content.innerHTML = `
            <div class="state-progress">
                <h3>🏛️ Футаба строит Государство Вугларст</h3>
                <p>Футаба сама ищет в интернете "как создать государство" и по пунктам создаёт документы...</p>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" id="progressBar" style="width: 0%;">0%</div>
                </div>
                <div id="buildStatus" style="margin-top: 1rem; color: var(--text-secondary);">
                    📡 Футаба начинает исследование...
                </div>
                <div class="progress-steps" id="progressSteps">
                    <div class="progress-step" id="step-1"><strong>📜 Конституция</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-2"><strong>📋 Декларация</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-3"><strong>⚖️ Гражданский кодекс</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-4"><strong>🔒 Уголовный кодекс</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-5"><strong>📝 Административный кодекс</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-6"><strong>💼 Трудовой кодекс</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-7"><strong>💰 Налоговый кодекс</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-8"><strong>🌍 Международное право</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-9"><strong>🎖️ Символы</strong><div class="step-status">Ожидание...</div></div>
                    <div class="progress-step" id="step-10"><strong>🎵 Гимн</strong><div class="step-status">Ожидание...</div></div>
                </div>
            </div>
        `;
        
        const docNames = ['Конституция', 'Декларация', 'Гражданский кодекс', 'Уголовный кодекс',
            'Административный кодекс', 'Трудовой кодекс', 'Налоговый кодекс',
            'Международное право', 'Символы', 'Гимн'];
        
        try {
            // Запускаем строительство — Футаба создаёт все документы
            const response = await fetch(`${this.apiBase}/api/vuglarst/build/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (data.status === 'ok') {
                // Анимация прогресса
                for (let i = 1; i <= 10; i++) {
                    const stepEl = document.getElementById(`step-${i}`);
                    if (stepEl) {
                        stepEl.classList.add('active');
                        stepEl.querySelector('.step-status').textContent = '🌐 Футаба ищет информацию...';
                        await new Promise(r => setTimeout(r, 300));
                        stepEl.querySelector('.step-status').textContent = '📝 Создание документа...';
                        await new Promise(r => setTimeout(r, 300));
                        stepEl.classList.remove('active');
                        stepEl.classList.add('completed');
                        stepEl.querySelector('.step-status').textContent = '✅ Создан';
                    }
                    const bar = document.getElementById('progressBar');
                    if (bar) {
                        const percent = (i / 10) * 100;
                        bar.style.width = `${percent}%`;
                        bar.textContent = `${percent}%`;
                    }
                }
                
                const status = document.getElementById('buildStatus');
                if (status) status.textContent = '✅ Футаба завершила строительство государства!';
                
                const results = data.results;
                content.innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">🏛️</div>
                        <h3 style="color: var(--accent-green); margin-bottom: 1rem;">Государство Вугларст создано Футабой!</h3>
                        <p style="margin-bottom: 1rem;">${data.message}</p>
                        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                            Футаба сама исследовала, создала и сохранила все документы государства.
                        </p>
                        <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: left;">
                            <strong>Созданные документы:</strong>
                            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                                ${results.documents.map(d => 
                                    `<li style="color: ${d.status === 'created' ? 'var(--accent-green)' : 'red'};">${d.name} — ${d.status === 'created' ? '✅' : '❌'}</li>`
                                ).join('')}
                            </ul>
                        </div>
                        <button class="btn btn-futaba" onclick="window.app.viewVuglarstDocuments()" style="padding: 1rem 2rem; font-size: 1.1rem;">
                            📖 Просмотреть документы государства
                        </button>
                    </div>
                `;
            } else {
                content.innerHTML = '<div class="loading">❌ Ошибка: ' + (data.error || 'неизвестно') + '</div>';
            }
        } catch (error) {
            console.error('Ошибка:', error);
            content.innerHTML = '<div class="loading">❌ Ошибка подключения к серверу</div>';
        }
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

    // ================================================================
    //  РЕДАКТОР ДОКУМЕНТОВ НОБУКИ
    // ================================================================

    async openNobukaEditor() {
        const modal = document.getElementById('nobukaEditorModal');
        const content = document.getElementById('nobukaEditorContent');
        if (!modal || !content) return;
        
        modal.style.display = 'block';
        content.innerHTML = '<div class="loading">📝 Нобука сканирует документы...</div>';
        
        try {
            // Загружаем статус и список документов параллельно
            const [statusRes, scanRes] = await Promise.all([
                fetch(`${this.apiBase}/api/nobuka/documents/status`),
                fetch(`${this.apiBase}/api/nobuka/documents/scan`)
            ]);
            
            const statusData = await statusRes.json();
            const scanData = await scanRes.json();
            
            if (statusData.status === 'ok' && scanData.status === 'ok') {
                this.renderNobukaEditor(content, statusData.editor, scanData.documents);
            } else {
                content.innerHTML = '<div class="loading">❌ Ошибка загрузки данных</div>';
            }
        } catch (error) {
            console.error('Ошибка:', error);
            content.innerHTML = '<div class="loading">❌ Ошибка подключения к серверу</div>';
        }
    }

    renderNobukaEditor(content, editorStatus, documents) {
        const m = editorStatus.metrics || {};
        const badgeClass = (ext) => {
            const map = {'.md': 'badge-md', '.json': 'badge-json', '.html': 'badge-html',
                         '.css': 'badge-css', '.js': 'badge-js', '.txt': 'badge-txt'};
            return map[ext] || 'badge-txt';
        };
        
        content.innerHTML = `
            <div class="doc-editor-toolbar">
                <button class="doc-editor-btn primary" id="nobukaImproveBtn">🚀 АвтоУлучшение</button>
                <button class="doc-editor-btn" id="nobukaHistoryBtn">📜 История</button>
                <button class="doc-editor-btn" id="nobukaBackupsBtn">💾 Резервные копии</button>
            </div>
            
            <div class="editor-stats">
                <div class="stat-card">
                    <div class="stat-card-value">${m.documents_scanned || 0}</div>
                    <div class="stat-card-label">Документов найдено</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value">${m.edits_applied || 0}</div>
                    <div class="stat-card-label">Улучшений применено</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value">${m.edits_rolled_back || 0}</div>
                    <div class="stat-card-label">Откатов</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value">${editorStatus.history_count || 0}</div>
                    <div class="stat-card-label">Всего операций</div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 1rem; color: var(--accent-purple);">📄 Документы проекта (${documents.length})</h3>
            <div class="doc-list" id="docList">
                ${documents.map(doc => `
                    <div class="doc-list-item" data-path="${doc.path}">
                        <div class="doc-list-item-info">
                            <div class="doc-list-item-name">${doc.filename}</div>
                            <div class="doc-list-item-meta">${doc.path} · ${doc.lines} строк · ${doc.size} символов</div>
                        </div>
                        <span class="doc-list-item-badge ${badgeClass(doc.extension)}">${doc.extension}</span>
                    </div>
                `).join('')}
            </div>
            
            <div id="docEditArea" style="display:none;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                    <h3 id="editDocTitle" style="color:var(--accent-purple);"></h3>
                    <button class="doc-editor-btn" id="closeEditBtn">← Назад к списку</button>
                </div>
                <textarea class="doc-edit-area" id="docEditTextarea" placeholder="Содержимое документа..."></textarea>
                <div style="display:flex;gap:0.5rem;margin-top:1rem;">
                    <button class="doc-editor-btn primary" id="saveDocBtn">💾 Сохранить (с проверкой)</button>
                    <button class="doc-editor-btn" id="cancelEditBtn">Отмена</button>
                </div>
                <div id="editResult"></div>
            </div>
        `;
        
        // Привязываем события
        this.bindNobukaEditorEvents(documents);
    }

    bindNobukaEditorEvents(documents) {
        // Клик по документу — открыть редактор
        document.querySelectorAll('.doc-list-item').forEach(item => {
            item.addEventListener('click', async () => {
                const path = item.dataset.path;
                await this.openDocForEdit(path);
            });
        });
        
        // АвтоУлучшение
        const improveBtn = document.getElementById('nobukaImproveBtn');
        if (improveBtn) {
            improveBtn.addEventListener('click', () => this.runAutoImprove());
        }
        
        // История
        const historyBtn = document.getElementById('nobukaHistoryBtn');
        if (historyBtn) {
            historyBtn.addEventListener('click', () => this.showEditHistory());
        }
        
        // Резервные копии
        const backupsBtn = document.getElementById('nobukaBackupsBtn');
        if (backupsBtn) {
            backupsBtn.addEventListener('click', () => this.showBackups());
        }
        
        // Кнопки редактора
        const closeEditBtn = document.getElementById('closeEditBtn');
        if (closeEditBtn) {
            closeEditBtn.addEventListener('click', () => {
                document.getElementById('docEditArea').style.display = 'none';
                document.getElementById('docList').style.display = 'grid';
            });
        }
        
        const saveDocBtn = document.getElementById('saveDocBtn');
        if (saveDocBtn) {
            saveDocBtn.addEventListener('click', () => this.saveDocEdit());
        }
        
        const cancelEditBtn = document.getElementById('cancelEditBtn');
        if (cancelEditBtn) {
            cancelEditBtn.addEventListener('click', () => {
                document.getElementById('docEditArea').style.display = 'none';
                document.getElementById('docList').style.display = 'grid';
            });
        }
    }

    async openDocForEdit(path) {
        try {
            const response = await fetch(`${this.apiBase}/api/nobuka/documents/read?path=${encodeURIComponent(path)}`);
            const data = await response.json();
            
            if (data.status === 'ok') {
                document.getElementById('docList').style.display = 'none';
                document.getElementById('docEditArea').style.display = 'block';
                document.getElementById('editDocTitle').textContent = `📝 ${path}`;
                document.getElementById('docEditTextarea').value = data.content;
                this._currentEditPath = path;
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    async saveDocEdit() {
        const path = this._currentEditPath;
        const content = document.getElementById('docEditTextarea').value;
        const resultDiv = document.getElementById('editResult');
        
        resultDiv.innerHTML = '<div class="edit-result warning">⏳ Нобука проверяет изменения...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/nobuka/documents/edit`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: path,
                    content: content,
                    reason: 'Ручное редактирование через интерфейс',
                    operator: 'user'
                })
            });
            const data = await response.json();
            
            if (data.status === 'ok') {
                const r = data.result;
                if (r.success) {
                    resultDiv.innerHTML = `<div class="edit-result success">✅ Документ сохранён! Размер: ${r.old_size} → ${r.new_size} символов. Проверки: ${r.test_report}</div>`;
                } else if (r.rolled_back) {
                    resultDiv.innerHTML = `<div class="edit-result error">↩️ Изменения отклонены и откачены. Причина: ${r.test_report || r.error}</div>`;
                } else {
                    resultDiv.innerHTML = `<div class="edit-result error">❌ Ошибка: ${r.error}</div>`;
                }
            }
        } catch (error) {
            resultDiv.innerHTML = `<div class="edit-result error">❌ Ошибка подключения: ${error}</div>`;
        }
    }

    async runAutoImprove() {
        const content = document.getElementById('nobukaEditorContent');
        content.innerHTML = '<div class="loading">🚀 Нобука улучшает документы...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/nobuka/documents/improve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (data.status === 'ok') {
                const results = data.results || [];
                const successCount = results.filter(r => r.success).length;
                const rollbackCount = results.filter(r => r.rolled_back).length;
                
                content.innerHTML = `
                    <div style="text-align:center;padding:2rem;">
                        <div style="font-size:3rem;margin-bottom:1rem;">📝</div>
                        <h3 style="color:var(--accent-purple);margin-bottom:1rem;">Нобука завершила автоУлучшение</h3>
                        <div class="editor-stats" style="max-width:600px;margin:0 auto 1.5rem;">
                            <div class="stat-card"><div class="stat-card-value">${results.length}</div><div class="stat-card-label">Обработано</div></div>
                            <div class="stat-card"><div class="stat-card-value" style="color:var(--accent-green);">${successCount}</div><div class="stat-card-label">Применено</div></div>
                            <div class="stat-card"><div class="stat-card-value" style="color:#e74c3c;">${rollbackCount}</div><div class="stat-card-label">Отклонено</div></div>
                        </div>
                        <div style="text-align:left;max-width:600px;margin:0 auto;">
                            ${results.map(r => `
                                <div class="edit-result ${r.success ? 'success' : (r.rolled_back ? 'error' : 'warning')}">
                                    ${r.success ? '✅' : (r.rolled_back ? '↩️' : '⚠️')} 
                                    <strong>${r.path}</strong> — ${r.reason || r.test_report || r.error}
                                </div>
                            `).join('')}
                        </div>
                        <button class="doc-editor-btn primary" onclick="window.app.openNobukaEditor()" style="margin-top:1.5rem;">← Назад</button>
                    </div>
                `;
            }
        } catch (error) {
            content.innerHTML = '<div class="loading">❌ Ошибка подключения</div>';
        }
    }

    async showEditHistory() {
        const content = document.getElementById('nobukaEditorContent');
        content.innerHTML = '<div class="loading">📜 Загрузка истории...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/nobuka/documents/history`);
            const data = await response.json();
            
            if (data.status === 'ok') {
                const history = data.history || [];
                content.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <h3 style="color:var(--accent-purple);">📜 История редактирований (${data.total})</h3>
                        <button class="doc-editor-btn" onclick="window.app.openNobukaEditor()">← Назад</button>
                    </div>
                    <div class="doc-list">
                        ${history.length === 0 ? '<div style="text-align:center;padding:2rem;color:var(--text-secondary);">История пуста</div>' :
                        history.slice().reverse().map(h => `
                            <div class="doc-list-item" style="cursor:default;">
                                <div class="doc-list-item-info">
                                    <div class="doc-list-item-name">${h.success ? '✅' : (h.rolled_back ? '↩️' : '❌')} ${h.path}</div>
                                    <div class="doc-list-item-meta">
                                        ${h.operator} · ${h.reason || ''} · ${h.timestamp ? new Date(h.timestamp).toLocaleString('ru-RU') : ''}
                                        ${h.test_report ? ' · ' + h.test_report : ''}
                                    </div>
                                </div>
                                <span class="doc-list-item-badge ${h.success ? 'badge-md' : 'badge-txt'}">
                                    ${h.success ? 'Применено' : (h.rolled_back ? 'Откат' : 'Ошибка')}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        } catch (error) {
            content.innerHTML = '<div class="loading">❌ Ошибка</div>';
        }
    }

    async showBackups() {
        const content = document.getElementById('nobukaEditorContent');
        content.innerHTML = '<div class="loading">💾 Загрузка резервных копий...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/nobuka/documents/backups`);
            const data = await response.json();
            
            if (data.status === 'ok') {
                const backups = data.backups || [];
                content.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <h3 style="color:var(--accent-purple);">💾 Резервные копии (${backups.length})</h3>
                        <button class="doc-editor-btn" onclick="window.app.openNobukaEditor()">← Назад</button>
                    </div>
                    <div class="doc-list">
                        ${backups.length === 0 ? '<div style="text-align:center;padding:2rem;color:var(--text-secondary);">Резервных копий нет</div>' :
                        backups.map(b => `
                            <div class="doc-list-item" style="cursor:default;">
                                <div class="doc-list-item-info">
                                    <div class="doc-list-item-name">${b.filename}</div>
                                    <div class="doc-list-item-meta">${b.size} байт · ${new Date(b.created).toLocaleString('ru-RU')}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        } catch (error) {
            content.innerHTML = '<div class="loading">❌ Ошибка</div>';
        }
    }

    async viewVuglarstDocuments() {        const modal = document.getElementById('futabaProfileModal');
        const content = document.getElementById('futabaProfileContent');
        if (!modal || !content) return;
        
        modal.style.display = 'block';
        content.innerHTML = '<div class="loading">🏛️ Загрузка документов Государства Вугларст...</div>';
        
        try {
            const response = await fetch(`${this.apiBase}/api/vuglarst/documents`);
            const data = await response.json();
            
            if (data.status === 'ok' && data.documents.length > 0) {
                content.innerHTML = `
                    <div class="work-header">
                        <button class="back-btn" style="background:none;border:none;color:var(--accent-blue);cursor:pointer;font-size:1rem;padding:0;margin-bottom:1rem;">← Назад</button>
                        <h2>🏛️ Государство Вугларст</h2>
                        <p class="work-subtitle">Документы суверенного цифрового государства</p>
                    </div>
                    <div class="tabs-container">
                        <div class="tab-buttons">
                            ${data.documents.map((doc, i) =>
                                `<button class="tab-btn ${i === 0 ? 'active' : ''}" data-tab="vug-tab-${i}">${doc.name}</button>`
                            ).join('')}
                        </div>
                        <div class="tab-panels">
                            ${data.documents.map((doc, i) =>
                                `<div class="tab-content ${i === 0 ? 'active' : ''}" id="vug-tab-${i}">
                                    <div class="doc-header"><h3>${doc.name}</h3><p class="doc-path">${doc.filename}</p></div>
                                    <div class="doc-content">${this.renderMarkdown(doc.content)}</div>
                                </div>`
                            ).join('')}
                        </div>
                    </div>
                `;
                setTimeout(() => {
                    this.bindTabs();
                    const backBtn = document.querySelector('.back-btn');
                    if (backBtn) backBtn.addEventListener('click', () => modal.style.display = 'none');
                }, 100);
            } else {
                content.innerHTML = '<div class="loading">❌ Документы государства не найдены. Сначала создайте государство.</div>';
            }
        } catch (error) {
            console.error('Ошибка загрузки документов государства:', error);
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
