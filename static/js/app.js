class LotteryApp {
    constructor() {
        this.sessionId = null;
        this.session = null;
        this.isBusy = false;
        this.elements = this.getElements();
        this.bindEvents();
        this.updateInputCount();
    }

    getElements() {
        const ids = [
            'setup-panel', 'lottery-panel', 'participant-input', 'input-count',
            'create-session-button', 'new-session-button', 'export-button',
            'total-count', 'remaining-count', 'drawn-count', 'draw-stage',
            'draw-result', 'draw-round', 'draw-button', 'reset-button',
            'participant-status', 'participants-grid', 'history-list',
            'history-empty', 'toast'
        ];
        return Object.fromEntries(ids.map(id => [id, document.getElementById(id)]));
    }

    bindEvents() {
        this.elements.participantInput.addEventListener('input', () => this.updateInputCount());
        this.elements.createSessionButton.addEventListener('click', () => this.createSession());
        this.elements.newSessionButton.addEventListener('click', () => this.showSetup());
        this.elements.exportButton.addEventListener('click', () => this.exportResults());
        this.elements.drawButton.addEventListener('click', () => this.draw());
        this.elements.resetButton.addEventListener('click', () => this.resetSession());
    }

    parseNames() {
        return this.elements.participantInput.value
            .split(/\r?\n/)
            .map(name => name.trim())
            .filter(Boolean);
    }

    updateInputCount() {
        this.elements.inputCount.textContent = `${this.parseNames().length} 人`;
    }

    async createSession() {
        const participants = this.parseNames();
        if (participants.length === 0) {
            this.showToast('请先输入参与者名单');
            return;
        }

        this.setButtonBusy(this.elements.createSessionButton, true, '创建中…');
        try {
            const result = await this.request('/api/lottery/sessions', {
                method: 'POST',
                body: JSON.stringify({ participants })
            });
            this.sessionId = result.data.session_id;
            this.session = result.data;
            this.renderSession();
            this.elements.setupPanel.classList.add('hidden');
            this.elements.lotteryPanel.classList.remove('hidden');
            this.showToast(`已创建 ${participants.length} 人抽奖场次`);
        } catch (error) {
            this.showToast(error.message);
        } finally {
            this.setButtonBusy(this.elements.createSessionButton, false, '创建抽奖');
        }
    }

    async draw() {
        if (!this.sessionId || this.isBusy || this.session.remaining_count === 0) return;

        this.isBusy = true;
        this.setButtonBusy(this.elements.drawButton, true, '抽取中…');
        this.elements.drawStage.classList.add('is-drawing');
        this.elements.drawResult.textContent = '正在抽取';
        this.elements.drawRound.textContent = '结果由服务端安全随机产生';

        try {
            const result = await this.request(`/api/lottery/sessions/${this.sessionId}/draw`, { method: 'POST' });
            this.session = await this.loadSession();
            this.elements.drawResult.textContent = result.data.winner.name;
            this.elements.drawRound.textContent = `第 ${result.data.record.round} 轮中奖`;
            this.renderSession();
        } catch (error) {
            this.showToast(error.message);
            this.elements.drawResult.textContent = '抽取失败';
        } finally {
            this.elements.drawStage.classList.remove('is-drawing');
            this.isBusy = false;
            this.updateDrawButton();
        }
    }

    async resetSession() {
        if (!this.sessionId || this.isBusy) return;
        if (!window.confirm('确定要清空本场中奖记录并重新开始吗？')) return;

        try {
            const result = await this.request(`/api/lottery/sessions/${this.sessionId}/reset`, { method: 'POST' });
            this.session = result.data;
            this.elements.drawResult.textContent = '准备开始';
            this.elements.drawRound.textContent = '本场已重置';
            this.renderSession();
            this.showToast('本场抽奖已重置');
        } catch (error) {
            this.showToast(error.message);
        }
    }

    async loadSession() {
        const result = await this.request(`/api/lottery/sessions/${this.sessionId}`);
        return result.data;
    }

    renderSession() {
        if (!this.session) return;
        const { total_count: total, remaining_count: remaining, drawn_count: drawn } = this.session;
        this.elements.totalCount.textContent = total;
        this.elements.remainingCount.textContent = remaining;
        this.elements.drawnCount.textContent = drawn;
        this.elements.participantStatus.textContent = remaining ? `还剩 ${remaining} 人` : '本场已抽完';
        this.renderParticipants();
        this.renderHistory();
        this.elements.exportButton.disabled = drawn === 0;
        this.updateDrawButton();
    }

    renderParticipants() {
        this.elements.participantsGrid.innerHTML = this.session.participants.map((participant, index) => `
            <div class="participant-card ${participant.is_winner ? 'is-winner' : ''}">
                <span class="participant-index">${String(index + 1).padStart(2, '0')}</span>
                <span class="participant-name">${this.escapeHtml(participant.name)}</span>
                <span class="participant-state">${participant.is_winner ? `第 ${participant.winner_round} 轮` : '待抽取'}</span>
            </div>
        `).join('');
    }

    renderHistory() {
        const history = this.session.history;
        this.elements.historyList.innerHTML = history.map(record => `
            <li class="history-item">
                <span class="history-round">${record.round}</span>
                <span class="history-name">${this.escapeHtml(record.winner.name)}</span>
                <time>${new Date(record.drawn_at).toLocaleString('zh-CN')}</time>
            </li>
        `).join('');
        this.elements.historyEmpty.classList.toggle('hidden', history.length > 0);
    }

    updateDrawButton() {
        const disabled = !this.session || this.isBusy || this.session.remaining_count === 0;
        this.elements.drawButton.disabled = disabled;
        this.elements.drawButton.textContent = this.session?.remaining_count === 0 ? '本场已抽完' : '开始抽一人';
    }

    showSetup() {
        this.sessionId = null;
        this.session = null;
        this.elements.participantInput.value = '';
        this.elements.lotteryPanel.classList.add('hidden');
        this.elements.setupPanel.classList.remove('hidden');
        this.elements.exportButton.disabled = true;
        this.updateInputCount();
        this.elements.participantInput.focus();
    }

    exportResults() {
        if (!this.session?.history.length) {
            this.showToast('暂无中奖记录');
            return;
        }
        const text = this.session.history
            .map(record => `第${record.round}轮：${record.winner.name}`)
            .join('\n');
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `抽奖结果-${new Date().toISOString().slice(0, 10)}.txt`;
        link.click();
        URL.revokeObjectURL(url);
    }

    async request(url, options = {}) {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
            ...options
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload?.success) {
            const message = payload?.detail?.error?.message || payload?.error?.message || '请求失败，请重试';
            throw new Error(message);
        }
        return payload;
    }

    setButtonBusy(button, busy, text) {
        button.disabled = busy;
        button.textContent = text;
    }

    showToast(message) {
        this.elements.toast.textContent = message;
        this.elements.toast.classList.add('is-visible');
        window.clearTimeout(this.toastTimer);
        this.toastTimer = window.setTimeout(() => this.elements.toast.classList.remove('is-visible'), 3500);
    }

    escapeHtml(value) {
        return value.replace(/[&<>'"]/g, character => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
        })[character]);
    }
}

document.addEventListener('DOMContentLoaded', () => new LotteryApp());
