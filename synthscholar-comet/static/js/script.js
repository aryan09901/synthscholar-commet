// SynthScholar - Frontend JavaScript
class SynthScholar {
    constructor() {
        this.currentAudio = null;
        this.isProcessing = false;
        this.initializeEventListeners();
        this.initializeDemoTopics();
        this.showWelcomeAnimation();
    }

    initializeEventListeners() {
        // Form submission
        const form = document.getElementById('researchForm');
        const topicInput = document.getElementById('topic');
        const newResearchBtn = document.getElementById('newResearchBtn');
        const retryBtn = document.getElementById('retryBtn');
        const useDemoMode = document.getElementById('useDemoMode');

        form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Character count for topic input
        topicInput.addEventListener('input', (e) => this.updateCharCount(e));
        
        if (newResearchBtn) {
            newResearchBtn.addEventListener('click', () => this.resetForm());
        }
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.resetForm());
        }

        // Audio player events
        this.setupAudioPlayer();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }

    initializeDemoTopics() {
        const demoTopics = document.querySelectorAll('.demo-topic');
        demoTopics.forEach(topic => {
            topic.addEventListener('click', (e) => {
                const topicText = e.currentTarget.getAttribute('data-topic');
                this.fillDemoTopic(topicText);
                this.highlightDemoTopic(e.currentTarget);
            });
        });
    }

    fillDemoTopic(topic) {
        const textarea = document.getElementById('topic');
        textarea.value = topic;
        textarea.focus();
        this.updateCharCount({ target: textarea });
        
        // Show success feedback
        this.showNotification(`Demo topic "${topic}" loaded!`, 'success');
    }

    highlightDemoTopic(selectedTopic) {
        // Remove highlight from all topics
        document.querySelectorAll('.demo-topic').forEach(topic => {
            topic.classList.remove('active');
        });
        
        // Add highlight to selected topic
        selectedTopic.classList.add('active');
    }

    updateCharCount(e) {
        const charCount = document.getElementById('charCount');
        const count = e.target.value.length;
        charCount.textContent = count;
        
        // Update color based on length
        if (count < 10) {
            charCount.style.color = '#ef4444';
        } else if (count < 30) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#10b981';
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isProcessing) {
            this.showNotification('Please wait for current process to complete', 'warning');
            return;
        }

        const topic = document.getElementById('topic').value.trim();
        
        if (!topic) {
            this.showError('Please enter a research topic.');
            return;
        }

        if (topic.length < 3) {
            this.showError('Please enter a topic with at least 3 characters.');
            return;
        }

        this.showLoading(true);
        this.hideResults();
        this.hideError();

        try {
            const response = await this.makeResearchRequest(topic);
            
            if (response.success) {
                this.showResults(response);
                this.showNotification('Podcast generated successfully!', 'success');
            } else {
                this.showError(response.error || 'An unexpected error occurred.');
            }
        } catch (error) {
            console.error('Research error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async makeResearchRequest(topic) {
        const response = await fetch('/api/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    showLoading(show) {
        const btn = document.getElementById('generateBtn');
        const btnText = btn.querySelector('.btn-text');
        const btnLoading = btn.querySelector('.btn-loading');
        const form = document.getElementById('researchForm');

        if (show) {
            this.isProcessing = true;
            btn.disabled = true;
            form.style.opacity = '0.7';
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            
            // Show processing animation
            this.showProcessingAnimation();
        } else {
            this.isProcessing = false;
            btn.disabled = false;
            form.style.opacity = '1';
            btnText.style.display = 'block';
            btnLoading.style.display = 'none';
            
            // Hide processing animation
            this.hideProcessingAnimation();
        }
    }

    showProcessingAnimation() {
        // Create processing steps animation
        const steps = [
            { icon: '🔍', text: 'Researching with COMET AI...', duration: 2000 },
            { icon: '✍️', text: 'Synthesizing content...', duration: 1500 },
            { icon: '🎧', text: 'Generating audio...', duration: 1000 }
        ];

        let currentStep = 0;
        
        const updateStep = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                this.updateProcessingStep(step.icon, step.text);
                currentStep++;
                setTimeout(updateStep, step.duration);
            }
        };
        
        updateStep();
    }

    updateProcessingStep(icon, text) {
        let stepIndicator = document.getElementById('processingSteps');
        if (!stepIndicator) {
            stepIndicator = document.createElement('div');
            stepIndicator.id = 'processingSteps';
            stepIndicator.className = 'processing-steps';
            document.querySelector('.research-card').appendChild(stepIndicator);
        }

        const stepElement = document.createElement('div');
        stepElement.className = 'processing-step active';
        stepElement.innerHTML = `
            <span class="step-icon">${icon}</span>
            <span class="step-text">${text}</span>
            <span class="step-spinner"></span>
        `;
        
        stepIndicator.appendChild(stepElement);
        
        // Scroll to show the current step
        stepElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    hideProcessingAnimation() {
        const stepIndicator = document.getElementById('processingSteps');
        if (stepIndicator) {
            stepIndicator.remove();
        }
    }

    showResults(data) {
        const resultDiv = document.getElementById('result');
        const audioPlayer = document.getElementById('audioPlayer');
        const scriptPreview = document.getElementById('scriptPreview');
        const downloadBtn = document.getElementById('downloadBtn');

        // Set audio source
        audioPlayer.src = data.audio_url;
        this.currentAudio = audioPlayer;
        
        // Set script preview with nice formatting
        scriptPreview.innerHTML = this.formatScriptPreview(data.script_preview);
        
        // Set download link
        const safeTopic = data.topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
        downloadBtn.href = data.audio_url;
        downloadBtn.download = `synthscholar_${safeTopic}.mp3`;
        downloadBtn.onclick = () => this.trackDownload(data.topic);

        // Show result section with animation
        resultDiv.style.display = 'block';
        setTimeout(() => {
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        // Auto-play audio if user prefers
        this.setupAutoPlay();
    }

    formatScriptPreview(script) {
        // Add basic formatting to script preview
        return script
            .split('\n')
            .map(line => {
                if (line.trim().startsWith('HOST:') || line.trim().startsWith('[')) {
                    return `<div class="script-highlight">${line}</div>`;
                }
                return `<div>${line}</div>`;
            })
            .join('');
    }

    setupAutoPlay() {
        // Check if user has previously allowed auto-play
        const autoPlayAllowed = localStorage.getItem('autoPlayAllowed');
        if (autoPlayAllowed === 'true' && this.currentAudio) {
            this.currentAudio.play().catch(e => {
                console.log('Auto-play prevented by browser');
            });
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('error');
        const errorMessage = document.getElementById('errorMessage');

        errorMessage.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Log error for analytics
        console.error('SynthScholar Error:', message);
    }

    hideResults() {
        const resultDiv = document.getElementById('result');
        resultDiv.style.display = 'none';
    }

    hideError() {
        const errorDiv = document.getElementById('error');
        errorDiv.style.display = 'none';
    }

    resetForm() {
        document.getElementById('researchForm').reset();
        this.hideResults();
        this.hideError();
        this.updateCharCount({ target: document.getElementById('topic') });
        
        // Reset demo topic highlights
        document.querySelectorAll('.demo-topic').forEach(topic => {
            topic.classList.remove('active');
        });
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Focus on topic input
        document.getElementById('topic').focus();
    }

    setupAudioPlayer() {
        const audioPlayer = document.getElementById('audioPlayer');
        if (audioPlayer) {
            audioPlayer.addEventListener('play', () => {
                this.trackPlayEvent();
            });
            
            audioPlayer.addEventListener('ended', () => {
                this.showNotification('Podcast finished! Ready for more learning? 🎓', 'success');
            });
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to submit form
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const form = document.getElementById('researchForm');
                if (form && !this.isProcessing) {
                    this.handleSubmit(new Event('submit'));
                }
            }
            
            // Escape to reset form
            if (e.key === 'Escape') {
                this.resetForm();
            }
        });
    }

    trackDownload(topic) {
        // Analytics tracking for downloads
        console.log('Download tracked:', topic);
        this.showNotification('Download started! 📥', 'success');
    }

    trackPlayEvent() {
        // Analytics tracking for audio plays
        console.log('Audio play tracked');
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notif => notif.remove());

        // Create new notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${this.getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: '💡'
        };
        return icons[type] || '💡';
    }

    showWelcomeAnimation() {
        // Show welcome message on first visit
        const firstVisit = !localStorage.getItem('synthscholar_visited');
        if (firstVisit) {
            setTimeout(() => {
                this.showNotification('Welcome to SynthScholar! Try a demo topic to get started 🚀', 'info');
                localStorage.setItem('synthscholar_visited', 'true');
            }, 1000);
        }
    }
}

// Additional utility functions
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show copy success notification
        const synthScholar = new SynthScholar();
        synthScholar.showNotification('Copied to clipboard! 📋', 'success');
    });
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.synthScholar = new SynthScholar();
    
    // Add custom styles for dynamic elements
    const style = document.createElement('style');
    style.textContent = `
        .processing-steps {
            margin: 20px 0;
            padding: 15px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        .processing-step {
            display: flex;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }
        
        .processing-step.active {
            background: rgba(99, 102, 241, 0.15);
            border-left: 3px solid #6366f1;
        }
        
        .step-icon {
            font-size: 1.2em;
            margin-right: 10px;
        }
        
        .step-text {
            flex: 1;
            font-weight: 500;
        }
        
        .step-spinner {
            width: 16px;
            height: 16px;
            border: 2px solid transparent;
            border-top: 2px solid #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 15px 20px;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
            max-width: 400px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            transform: translateX(400px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .notification.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .notification-success {
            border-left: 4px solid #10b981;
        }
        
        .notification-error {
            border-left: 4px solid #ef4444;
        }
        
        .notification-warning {
            border-left: 4px solid #f59e0b;
        }
        
        .notification-info {
            border-left: 4px solid #6366f1;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .notification-close:hover {
            color: white;
        }
        
        .script-highlight {
            background: rgba(99, 102, 241, 0.1);
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 3px solid #6366f1;
            font-weight: 500;
        }
        
        .demo-topic.active {
            background: linear-gradient(135deg, #6366f1 0%, #10b981 100%) !important;
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .notification {
                top: 10px;
                right: 10px;
                left: 10px;
                max-width: none;
            }
        }
    `;
    document.head.appendChild(style);
    
    console.log('🎧 SynthScholar initialized successfully!');
});

// Error boundary for the application
window.addEventListener('error', (e) => {
    console.error('Application error:', e.error);
    
    // Show user-friendly error message
    if (window.synthScholar) {
        window.synthScholar.showError('Something went wrong. Please refresh the page and try again.');
    }
});