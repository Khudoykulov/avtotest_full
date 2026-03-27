// Quiz functionality for Auto Test platform
class QuizApp {
    constructor() {
        this.currentQuestion = 0;
        this.answers = {};
        this.timer = null;
        this.timeLeft = 1800; // 30 minutes
        this.init();
    }

    init() {
        this.startTimer();
        this.bindEvents();
        this.updateQuestionCounter();
    }

    bindEvents() {
        // Answer selection
        document.querySelectorAll('.answer-option').forEach(option => {
            option.addEventListener('click', (e) => {
                this.selectAnswer(e.target);
            });
        });

        // Navigation buttons
        document.getElementById('next-btn')?.addEventListener('click', () => {
            this.nextQuestion();
        });

        document.getElementById('prev-btn')?.addEventListener('click', () => {
            this.prevQuestion();
        });

        document.getElementById('submit-btn')?.addEventListener('click', () => {
            this.submitTest();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case '1':
                case '2':
                case '3':
                case '4':
                    if (e.target.tagName !== 'INPUT') {
                        const options = document.querySelectorAll('.answer-option');
                        if (options[e.key - 1]) {
                            this.selectAnswer(options[e.key - 1]);
                        }
                    }
                    break;
                case 'ArrowRight':
                    if (e.target.tagName !== 'INPUT') {
                        e.preventDefault();
                        this.nextQuestion();
                    }
                    break;
                case 'ArrowLeft':
                    if (e.target.tagName !== 'INPUT') {
                        e.preventDefault();
                        this.prevQuestion();
                    }
                    break;
            }
        });
    }

    selectAnswer(element) {
        const questionId = element.dataset.questionId;
        const answerId = element.dataset.answerId;

        // Remove previous selections
        document.querySelectorAll(`[data-question-id="${questionId}"]`).forEach(opt => {
            opt.classList.remove('selected');
        });

        // Add selection to clicked option
        element.classList.add('selected');
        
        // Store answer
        this.answers[questionId] = answerId;
        
        // Update progress
        this.updateProgress();
    }

    nextQuestion() {
        const questions = document.querySelectorAll('.question-card');
        if (this.currentQuestion < questions.length - 1) {
            questions[this.currentQuestion].style.display = 'none';
            this.currentQuestion++;
            questions[this.currentQuestion].style.display = 'block';
            this.updateQuestionCounter();
            this.updateNavigationButtons();
        }
    }

    prevQuestion() {
        const questions = document.querySelectorAll('.question-card');
        if (this.currentQuestion > 0) {
            questions[this.currentQuestion].style.display = 'none';
            this.currentQuestion--;
            questions[this.currentQuestion].style.display = 'block';
            this.updateQuestionCounter();
            this.updateNavigationButtons();
        }
    }

    updateQuestionCounter() {
        const counter = document.getElementById('question-counter');
        const total = document.querySelectorAll('.question-card').length;
        if (counter) {
            counter.textContent = `Savol ${this.currentQuestion + 1} / ${total}`;
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const submitBtn = document.getElementById('submit-btn');
        const total = document.querySelectorAll('.question-card').length;

        if (prevBtn) {
            prevBtn.style.display = this.currentQuestion > 0 ? 'inline-block' : 'none';
        }

        if (this.currentQuestion === total - 1) {
            if (nextBtn) nextBtn.style.display = 'none';
            if (submitBtn) submitBtn.style.display = 'inline-block';
        } else {
            if (nextBtn) nextBtn.style.display = 'inline-block';
            if (submitBtn) submitBtn.style.display = 'none';
        }
    }

    updateProgress() {
        const totalQuestions = document.querySelectorAll('.question-card').length;
        const answeredQuestions = Object.keys(this.answers).length;
        const percentage = (answeredQuestions / totalQuestions) * 100;
        
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }

        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.textContent = `${answeredQuestions} / ${totalQuestions} javob berildi`;
        }
    }

    startTimer() {
        const timerElement = document.getElementById('timer');
        if (!timerElement) return;

        this.timer = setInterval(() => {
            this.timeLeft--;
            
            const hours = Math.floor(this.timeLeft / 3600);
            const minutes = Math.floor((this.timeLeft % 3600) / 60);
            const seconds = this.timeLeft % 60;
            
            const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            timerElement.textContent = timeString;
            
            // Change color when time is running out
            if (this.timeLeft < 300) { // 5 minutes
                timerElement.style.color = '#e74c3c';
                timerElement.style.backgroundColor = '#ffebee';
            } else if (this.timeLeft < 600) { // 10 minutes
                timerElement.style.color = '#f39c12';
                timerElement.style.backgroundColor = '#fff8e1';
            }
            
            // Auto-submit when time runs out
            if (this.timeLeft <= 0) {
                clearInterval(this.timer);
                this.submitTest();
            }
        }, 1000);
    }

    async submitTest() {
        if (Object.keys(this.answers).length === 0) {
            if (!confirm('Hech qanday savol javob berilmagan. Testni tugatmoqchimisiz?')) {
                return;
            }
        }

        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.textContent = 'Yuborilmoqda...';
            submitBtn.disabled = true;
        }

        try {
            const timeSpent = 1800 - this.timeLeft; // Total time - time left
            const testData = {
                answers: this.answers,
                time_taken: timeSpent,
                test_type: this.getTestType(),
                ticket_id: this.getTicketId(),
                category_id: this.getCategoryId()
            };

            const response = await fetch('/quiz/submit-test/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(testData)
            });

            const result = await response.json();
            
            if (result.success) {
                clearInterval(this.timer);
                window.location.href = `/quiz/results/${result.result_id}/`;
            } else {
                alert('Xatolik yuz berdi. Iltimos qayta urinib ko\'ring.');
                if (submitBtn) {
                    submitBtn.textContent = 'Testni tugatish';
                    submitBtn.disabled = false;
                }
            }
        } catch (error) {
            console.error('Error submitting test:', error);
            alert('Xatolik yuz berdi. Iltimos qayta urinib ko\'ring.');
            if (submitBtn) {
                submitBtn.textContent = 'Testni tugatish';
                submitBtn.disabled = false;
            }
        }
    }

    getTestType() {
        const testTypeElement = document.getElementById('test-type');
        return testTypeElement ? testTypeElement.value : 'category';
    }

    getTicketId() {
        const ticketIdElement = document.getElementById('ticket-id');
        return ticketIdElement ? ticketIdElement.value : null;
    }

    getCategoryId() {
        const categoryIdElement = document.getElementById('category-id');
        return categoryIdElement ? categoryIdElement.value : null;
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Statistics Chart functionality
class StatsChart {
    static renderProgressChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Set styles
        ctx.fillStyle = '#667eea';
        ctx.strokeStyle = '#764ba2';
        ctx.lineWidth = 2;

        // Draw bars
        const barWidth = width / data.length - 10;
        const maxValue = Math.max(...data.map(item => item.value));

        data.forEach((item, index) => {
            const barHeight = (item.value / maxValue) * (height - 40);
            const x = index * (barWidth + 10) + 5;
            const y = height - barHeight - 20;

            // Draw bar
            ctx.fillRect(x, y, barWidth, barHeight);

            // Draw label
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(item.label, x + barWidth / 2, height - 5);

            // Draw value
            ctx.fillText(item.value.toString(), x + barWidth / 2, y - 5);
            
            ctx.fillStyle = '#667eea';
        });
    }

    static renderPieChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const total = data.reduce((sum, item) => sum + item.value, 0);
        let currentAngle = -Math.PI / 2; // Start from top

        const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c'];

        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * 2 * Math.PI;
            
            // Draw slice
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = colors[index % colors.length];
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Draw label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius + 30);
            const labelY = centerY + Math.sin(labelAngle) * (radius + 30);
            
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(item.label, labelX, labelY);
            ctx.fillText(`${item.value}`, labelX, labelY + 15);

            currentAngle += sliceAngle;
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize quiz if on quiz page
    if (document.querySelector('.question-card')) {
        new QuizApp();
    }

    // Initialize charts if on statistics page
    const progressData = window.progressData;
    const categoryData = window.categoryData;
    
    if (progressData) {
        StatsChart.renderProgressChart('progress-chart', progressData);
    }
    
    if (categoryData) {
        StatsChart.renderPieChart('category-chart', categoryData);
    }
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Add smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});