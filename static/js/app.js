class LotteryApp {
    constructor() {
        this.participants = [];
        this.winners = [];
        this.isLotteryInProgress = false;
        
        this.initElements();
        this.bindEvents();
    }
    
    initElements() {
        this.uploadArea = document.getElementById('upload-area');
        this.uploadContent = document.getElementById('upload-content');
        this.uploadProgress = document.getElementById('upload-progress');
        this.fileInput = document.getElementById('file-input');
        
        this.lotteryArea = document.getElementById('lottery-area');
        this.participantsGrid = document.getElementById('participants-grid');
        
        this.btnReupload = document.getElementById('btn-reupload');
        this.btnExport = document.getElementById('btn-export');
        this.btnLottery = document.getElementById('btn-lottery');
        
        this.winnersSection = document.getElementById('winners-section');
        this.winnersList = document.getElementById('winners-list');
        
        this.statusBar = document.getElementById('status-bar');
        this.totalCount = document.getElementById('total-count');
        this.drawnCount = document.getElementById('drawn-count');
        
        this.winnerModal = document.getElementById('winner-modal');
        this.winnerAvatarImg = document.getElementById('winner-avatar-img');
        this.winnerName = document.getElementById('winner-name');
        this.winnerRound = document.getElementById('winner-round');
        
        this.btnContinue = document.getElementById('btn-continue');
        this.btnViewWinners = document.getElementById('btn-view-winners');
        
        this.errorToast = document.getElementById('error-toast');
        this.errorMessage = document.getElementById('error-message');
    }
    
    bindEvents() {
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        this.btnReupload.addEventListener('click', () => this.resetToUpload());
        this.btnExport.addEventListener('click', () => this.exportResults());
        
        this.btnLottery.addEventListener('click', () => this.startLottery());
        
        this.btnContinue.addEventListener('click', () => this.hideWinnerModal());
        this.btnViewWinners.addEventListener('click', () => this.showWinnersAndHideModal());
        
        this.winnerModal.querySelector('.modal-backdrop').addEventListener('click', () => this.hideWinnerModal());
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }
    
    async uploadFile(file) {
        this.showProgress();
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/lottery/participants', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.participants = result.data.participants;
                this.showLotteryArea();
            } else {
                this.showError(result.error.message);
            }
        } catch (error) {
            this.showError('上传失败，请重试');
        } finally {
            this.hideProgress();
        }
    }
    
    showProgress() {
        this.uploadContent.style.display = 'none';
        this.uploadProgress.style.display = 'flex';
        
        let progress = 0;
        this.progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                document.getElementById('progress-fill').style.width = progress + '%';
            }
        }, 200);
    }
    
    hideProgress() {
        clearInterval(this.progressInterval);
        document.getElementById('progress-fill').style.width = '100%';
        
        setTimeout(() => {
            this.uploadProgress.style.display = 'none';
            this.uploadContent.style.display = 'flex';
        }, 500);
    }
    
    showLotteryArea() {
        this.uploadArea.style.display = 'none';
        this.lotteryArea.style.display = 'block';
        this.statusBar.style.display = 'flex';
        this.btnReupload.style.display = 'block';
        this.btnExport.style.display = 'block';
        
        this.renderParticipants();
        this.updateStatus();
    }
    
    renderParticipants() {
        this.participantsGrid.innerHTML = '';
        
        this.participants.forEach((participant, index) => {
            const card = document.createElement('div');
            card.className = 'avatar-card';
            card.dataset.id = participant.id;
            
            if (participant.is_winner) {
                card.classList.add('eliminated');
            }
            
            card.innerHTML = `
                <img class="avatar-image" src="${participant.avatar_base64}" alt="${participant.name}的头像">
                <div class="avatar-name">${participant.name}</div>
            `;
            
            this.participantsGrid.appendChild(card);
        });
    }
    
    updateStatus() {
        this.totalCount.textContent = this.participants.length;
        this.drawnCount.textContent = this.participants.filter(p => p.is_winner).length;
        
        const remaining = this.participants.filter(p => !p.is_winner).length;
        if (remaining < 2) {
            this.btnLottery.disabled = true;
            this.btnLottery.innerHTML = '<span>🎉</span> 抽奖结束';
        }
    }
    
    async startLottery() {
        if (this.isLotteryInProgress) return;
        if (this.participants.filter(p => !p.is_winner).length < 2) return;
        
        this.isLotteryInProgress = true;
        this.btnLottery.disabled = true;
        this.btnLottery.classList.add('loading');
        
        await this.playAnimation();
        
        try {
            const response = await fetch('/api/lottery/draw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const winner = result.data.winner;
                this.updateParticipantWinner(winner);
                this.showWinnerModal(winner, result.data.draw_number);
            } else {
                this.showError(result.error.message);
            }
        } catch (error) {
            this.showError('抽奖失败，请重试');
        } finally {
            this.isLotteryInProgress = false;
            this.btnLottery.classList.remove('loading');
            this.updateStatus();
            
            const remaining = this.participants.filter(p => !p.is_winner).length;
            if (remaining >= 2) {
                this.btnLottery.disabled = false;
            }
        }
    }
    
    async playAnimation() {
        const remainingParticipants = this.participants.filter(p => !p.is_winner);
        const cards = Array.from(this.participantsGrid.querySelectorAll('.avatar-card'));
        const remainingCards = cards.filter(card => {
            const participant = this.participants.find(p => p.id === card.dataset.id);
            return participant && !participant.is_winner;
        });
        
        await this.fastBlink(remainingCards, 1000);
        
        await this.slowDown(remainingCards, 1500);
    }
    
    fastBlink(cards, duration) {
        return new Promise(resolve => {
            const interval = setInterval(() => {
                cards.forEach(card => {
                    card.classList.toggle('avatar-blinking');
                });
            }, 100);
            
            setTimeout(() => {
                clearInterval(interval);
                cards.forEach(card => {
                    card.classList.remove('avatar-blinking');
                });
                resolve();
            }, duration);
        });
    }
    
    slowDown(cards, duration) {
        return new Promise(resolve => {
            let step = 0;
            const intervals = [200, 300, 400];
            
            const runStep = () => {
                if (step >= intervals.length) {
                    resolve();
                    return;
                }
                
                cards.forEach(card => {
                    card.classList.add('avatar-slow-blink');
                });
                
                setTimeout(() => {
                    cards.forEach(card => {
                        card.classList.remove('avatar-slow-blink');
                    });
                    
                    step++;
                    if (step < intervals.length) {
                        setTimeout(runStep, 100);
                    } else {
                        resolve();
                    }
                }, intervals[step - 1]);
            };
            
            runStep();
        });
    }
    
    updateParticipantWinner(winner) {
        const index = this.participants.findIndex(p => p.id === winner.id);
        if (index !== -1) {
            this.participants[index].is_winner = true;
            this.participants[index].winner_round = winner.winner_round;
        }
        
        this.renderParticipants();
        
        const winnerCard = this.participantsGrid.querySelector(`[data-id="${winner.id}"]`);
        if (winnerCard) {
            winnerCard.classList.add('avatar-explode');
        }
        
        this.winners.push(winner);
        this.updateWinnersSection();
    }
    
    updateWinnersSection() {
        if (this.winners.length === 0) {
            this.winnersSection.style.display = 'none';
            return;
        }
        
        this.winnersSection.style.display = 'block';
        this.winnersList.innerHTML = '';
        
        this.winners.forEach(winner => {
            const item = document.createElement('div');
            item.className = 'winner-item';
            item.innerHTML = `
                <img class="avatar-image" src="${winner.avatar_base64}" alt="${winner.name}">
                <div class="avatar-name">${winner.name}</div>
                <div class="round-tag">第${winner.winner_round}轮</div>
            `;
            this.winnersList.appendChild(item);
        });
    }
    
    showWinnerModal(winner, drawNumber) {
        this.winnerAvatarImg.src = winner.avatar_base64;
        this.winnerName.textContent = winner.name;
        this.winnerRound.textContent = `第 ${drawNumber} 轮中奖`;
        
        this.winnerModal.style.display = 'flex';
    }
    
    hideWinnerModal() {
        this.winnerModal.style.display = 'none';
        
        const winnerCards = this.participantsGrid.querySelectorAll('.avatar-explode');
        winnerCards.forEach(card => {
            card.classList.remove('avatar-explode');
            card.classList.add('eliminated');
        });
    }
    
    showWinnersAndHideModal() {
        this.hideWinnerModal();
        
        this.winnersSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    resetToUpload() {
        this.participants = [];
        this.winners = [];
        
        this.lotteryArea.style.display = 'none';
        this.uploadArea.style.display = 'block';
        this.statusBar.style.display = 'none';
        this.btnReupload.style.display = 'none';
        this.btnExport.style.display = 'none';
        this.winnersSection.style.display = 'none';
        
        this.fileInput.value = '';
    }
    
    exportResults() {
        if (this.winners.length === 0) {
            this.showError('暂无中奖者');
            return;
        }
        
        const text = this.winners.map((w, i) => `${i + 1}. ${w.name}`).join('\n');
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                alert('中奖名单已复制到剪贴板');
            }).catch(() => {
                this.fallbackCopy(text);
            });
        } else {
            this.fallbackCopy(text);
        }
    }
    
    fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('中奖名单已复制到剪贴板');
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorToast.style.display = 'block';
        
        setTimeout(() => {
            this.errorToast.style.display = 'none';
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new LotteryApp();
});