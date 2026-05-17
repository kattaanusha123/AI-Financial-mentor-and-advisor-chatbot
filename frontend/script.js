const API_BASE_URL = 'http://localhost:5000/api';
let accessToken = localStorage.getItem('accessToken');
let isRecording = false, recognition = null;
let voiceResponseEnabled = localStorage.getItem('voiceResponse') === 'true';
let currentLanguage = localStorage.getItem('preferredLanguage') || 'en';
let synth = window.speechSynthesis;

document.addEventListener('DOMContentLoaded', () => {
    // Show login modal if not authenticated; otherwise load profile
    if (accessToken) {
        loadUserProfile();
    } else {
        showLoginModal();
    }
    initVoiceRecognition();
    setupModalClose();
    setupFormHandlers();
    updateAuthButtons();
});

function showLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
    document.getElementById('mainContainer').style.display = 'none';
}

function hideLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function setupModalClose() {
    const modal = document.getElementById('loginModal');
    document.querySelector('.close').onclick = hideLoginModal;
    window.onclick = (e) => { if (e.target === modal) hideLoginModal(); };
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    const isLogin = tabName === 'login';
    document.getElementById(isLogin ? 'loginTab' : 'registerTab').classList.add('active');
    document.querySelectorAll('.tab-button')[isLogin ? 0 : 1].classList.add('active');
}

function showMainContainer() {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('mainContainer').style.display = 'block';
    // main container visible; profile will be loaded where appropriate
    updateAuthButtons();
}

function updateAuthButtons() {
    const loginBtn = document.getElementById('loginHeaderBtn');
    const registerBtn = document.getElementById('registerHeaderBtn');
    const logoutBtn = document.querySelector('.btn-danger');
    if (accessToken) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (registerBtn) registerBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-flex';
    } else {
        if (loginBtn) loginBtn.style.display = 'inline-flex';
        if (registerBtn) registerBtn.style.display = 'inline-flex';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}


function setupFormHandlers() {
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            accessToken = data.access_token;
            localStorage.setItem('accessToken', accessToken);
            showMainContainer();
            updateAuthButtons();
            // Migrate any guest history to the server after successful login
            try { migrateGuestHistoryIfAny(); } catch (err) { console.error('Migration error:', err); }
            showNotification('Login successful!', 'success');
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Login error:', error);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await response.json();
        if (response.ok) {
            accessToken = data.access_token;
            localStorage.setItem('accessToken', accessToken);
            showMainContainer();
            updateAuthButtons();
            // Migrate guest history on successful registration
            try { migrateGuestHistoryIfAny(); } catch (err) { console.error('Migration error:', err); }
            showNotification('Registration successful!', 'success');
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Register error:', error);
    }
}

function logout() {
    accessToken = null;
    localStorage.removeItem('accessToken');
    showLoginModal();
    showNotification('Logged out successfully', 'success');
    updateAuthButtons();
}

async function loadUserProfile() {
    if (!accessToken) { showLoginModal(); return; }
    try {
        const response = await fetch(`${API_BASE_URL}/user`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (response.ok) {
            if (data.user && data.user.preferred_language) {
                currentLanguage = data.user.preferred_language;
                localStorage.setItem('preferredLanguage', currentLanguage);
                const langSelector = document.getElementById('languageSelector');
                if (langSelector) langSelector.value = currentLanguage;
            }
                showMainContainer();
                updateAuthButtons();
            // sidebar not used — keeping original single-pane layout
        } else if (response.status === 422 || response.status === 401) {
            console.error('Token validation failed:', data);
            localStorage.removeItem('accessToken');
            accessToken = null;
            showLoginModal();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        showLoginModal();
    }
}

// Profile UI removed; explicit profile persistence has been reverted.

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;
    addMessageToChat(message, 'user');
    input.value = '';
    try {
        const headers = { 'Content-Type': 'application/json' };
        if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;

        // Build payload (keep previous behavior: do not send local guest history)
        const payload = { query: message, language: currentLanguage };
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (response.ok) {
            addMessageToChat(data.response, 'bot');
                // Save guest chat locally when user is not authenticated
                if (!accessToken) {
                    try {
                        const entry = {
                            query: message,
                            response: data.response,
                            timestamp: new Date().toISOString(),
                            type: data.type || 'general'
                        };
                        const existing = JSON.parse(localStorage.getItem('guestHistory') || '[]');
                        existing.push(entry);
                        if (existing.length > 200) existing.splice(0, existing.length - 200);
                        localStorage.setItem('guestHistory', JSON.stringify(existing));
                        // guest history saved (no sidebar to update in single-pane layout)
                    } catch (err) {
                        console.error('Failed to save guest history:', err);
                    }
                }
            if (voiceResponseEnabled) speakText(data.response);
        } else {
            if (response.status === 401 || response.status === 422) {
                logout();
                showNotification('Session expired. Please login again.', 'error');
            } else {
                addMessageToChat(data.error || 'Unable to process your request', 'bot');
            }
        }
    } catch (error) {
        addMessageToChat('Error connecting to server. Please check if the backend is running.', 'bot');
        console.error('Chat error:', error);
    }
}

function addMessageToChat(message, type) {
    const chatMessages = document.getElementById('chatMessages');
    // Build group wrapper to match CSS: .message-group.{user-group|bot-group}
    const groupDiv = document.createElement('div');
    groupDiv.className = `message-group ${type === 'user' ? 'user-group' : 'bot-group'}`;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type === 'user' ? 'user-message' : 'bot-message'}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = type === 'user' ? 'You' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(message);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    groupDiv.appendChild(messageDiv);
    chatMessages.appendChild(groupDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Personalized allocation rendering removed per user request.

function formatMessage(text) {
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/(^|[^*])\*([^*].*?[^*])\*([^*]|$)/g, '$1<em>$2</em>$3');
    const paragraphs = text.split(/\n\s*\n/);
    let html = '';
    let currentListType = null;
    
    paragraphs.forEach(para => {
        para = para.trim();
        if (!para) return;
        const lines = para.split(/\n/);
        lines.forEach(line => {
            line = line.trim();
            if (!line) return;
            if (line.match(/^[•\*]\s+/)) {
                if (currentListType !== 'ul') {
                    if (currentListType) html += currentListType === 'ol' ? '</ol>' : '</ul>';
                    html += '<ul style="margin: 8px 0; padding-left: 20px;">';
                    currentListType = 'ul';
                }
                html += `<li style="margin: 4px 0;">${line.replace(/^[•\*]\s+/, '')}</li>`;
            } else if (line.match(/^\d+\.\s+/)) {
                if (currentListType !== 'ol') {
                    if (currentListType) html += currentListType === 'ol' ? '</ol>' : '</ul>';
                    html += '<ol style="margin: 8px 0; padding-left: 20px;">';
                    currentListType = 'ol';
                }
                html += `<li style="margin: 4px 0;">${line.replace(/^\d+\.\s+/, '')}</li>`;
            } else {
                if (currentListType) {
                    html += currentListType === 'ol' ? '</ol>' : '</ul>';
                    currentListType = null;
                }
                html += `<p style="margin: 8px 0;">${line}</p>`;
            }
        });
    });
    if (currentListType) html += currentListType === 'ol' ? '</ol>' : '</ul>';
    return html || `<p>${text.replace(/\n/g, '<br>')}</p>`;
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// History view - show saved history (server for authenticated users, localStorage for guests)
function showHistory() {
    // Hide other sections
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById('historySection').style.display = 'block';
    document.getElementById('chartsSection').style.display = 'none';
    document.getElementById('marketSection').style.display = 'none';
    document.getElementById('calculatorSection').style.display = 'none';
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '<p>Loading history...</p>';

    if (accessToken) {
        // Fetch from server
        fetch(`${API_BASE_URL}/history?limit=200`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' }
        }).then(r => r.json()).then(data => {
            const list = data.history || [];
            if (!list.length) {
                historyContent.innerHTML = '<p>No conversation history yet.</p>';
                return;
            }
            historyContent.innerHTML = '';
            list.forEach(entry => {
                const div = document.createElement('div');
                div.className = 'history-entry';
                div.innerHTML = `<div class="history-time">${new Date(entry.timestamp).toLocaleString()}</div><div class="history-query"><strong>You:</strong> ${entry.query}</div><div class="history-response"><strong>Bot:</strong> ${entry.response}</div>`;
                historyContent.appendChild(div);
            });
        }).catch(err => {
            console.error('Failed to fetch history:', err);
            historyContent.innerHTML = '<p>Unable to load history.</p>';
        });
    } else {
        // Load from localStorage
        try {
            const existing = JSON.parse(localStorage.getItem('guestHistory') || '[]');
            if (!existing.length) {
                historyContent.innerHTML = '<p>No conversation history yet.</p>';
                return;
            }
            historyContent.innerHTML = '';
            existing.slice().reverse().forEach(entry => {
                const div = document.createElement('div');
                div.className = 'history-entry';
                div.innerHTML = `<div class="history-time">${new Date(entry.timestamp).toLocaleString()}</div><div class="history-query"><strong>You:</strong> ${entry.query}</div><div class="history-response"><strong>Bot:</strong> ${entry.response}</div>`;
                historyContent.appendChild(div);
            });
        } catch (err) {
            console.error('Failed to load guest history:', err);
            historyContent.innerHTML = '<p>Unable to load history.</p>';
        }
    }
}

// Migrate guest history from localStorage to server for authenticated users
async function migrateGuestHistoryIfAny() {
    try {
        const raw = localStorage.getItem('guestHistory');
        if (!raw) return;
        const entries = JSON.parse(raw || '[]');
        if (!entries || !entries.length) return;
        if (!accessToken) return;

        // Send entries in batches to avoid too-large requests
        const batchSize = 100;
        let importedTotal = 0;
        for (let i = 0; i < entries.length; i += batchSize) {
            // send only the necessary fields when importing guest history
            const batch = entries.slice(i, i + batchSize).map(e => ({ query: e.query, response: e.response, timestamp: e.timestamp, type: e.type }));
            const resp = await fetch(`${API_BASE_URL}/history/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}` },
                body: JSON.stringify({ entries: batch })
            });
            if (resp.ok) {
                const data = await resp.json();
                importedTotal += data.imported || 0;
            } else {
                console.error('Failed to import batch', resp.status);
                break;
            }
        }

        // Clear guest history only if something was imported
        if (importedTotal > 0) {
            localStorage.removeItem('guestHistory');
            showNotification(`Imported ${importedTotal} chat messages to your account`, 'success');
        }
    } catch (err) {
        console.error('Error migrating guest history:', err);
    }
}

// Voice Recognition
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            sendMessage();
        };
        
        recognition.onerror = (event) => {
            // Only show notification for errors that matter, not for 'no-speech'
            if (event.error !== 'no-speech') {
                console.error('Speech recognition error:', event.error);
                showNotification('Voice recognition error', 'error');
            } else {
                // 'no-speech' is normal when user doesn't speak or mic times out
                console.log('No speech detected - user may not have spoken');
            }
            stopVoiceRecognition();
        };
        
        recognition.onend = () => {
            stopVoiceRecognition();
        };
    } else {
        document.getElementById('voiceBtn').style.display = 'none';
        console.warn('Speech recognition not supported');
    }
}

function startVoiceRecognition() {
    if (!recognition) {
        showNotification('Voice recognition not supported in this browser', 'error');
        return;
    }
    
    if (isRecording) {
        stopVoiceRecognition();
    } else {
        try {
            recognition.start();
            isRecording = true;
            document.getElementById('voiceBtn').classList.add('recording');
            showNotification('Listening...', 'info');
        } catch (error) {
            console.error('Error starting recognition:', error);
        }
    }
}

function stopVoiceRecognition() {
    if (recognition && isRecording) {
        recognition.stop();
        isRecording = false;
        document.getElementById('voiceBtn').classList.remove('recording');
    }
}

// Calculator Functions
function showCalculator() {
    document.getElementById('chatSection').style.display = 'none';
    document.getElementById('marketSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'none';
    document.getElementById('calculatorSection').style.display = 'block';
}

function closeCalculator() {
    document.getElementById('calculatorSection').style.display = 'none';
    document.getElementById('chatSection').style.display = 'block';
}

function showCalcTab(tab) {
    // Hide all calc tabs
    document.querySelectorAll('.calc-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active from all calc tab buttons
    document.querySelectorAll('.calc-tab').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    let tabId = '';
    let tabIndex = 0;
    
    switch(tab) {
        case 'emi':
            tabId = 'emiCalc';
            tabIndex = 0;
            break;
        case 'sip':
            tabId = 'sipCalc';
            tabIndex = 1;
            break;
        case 'compound':
            tabId = 'compoundCalc';
            tabIndex = 2;
            break;
        case 'simple':
            tabId = 'simpleCalc';
            tabIndex = 3;
            break;
    }
    
    document.getElementById(tabId).classList.add('active');
    document.querySelectorAll('.calc-tab')[tabIndex].classList.add('active');
}

async function calculateEMI() {
    const principal = parseFloat(document.getElementById('emiPrincipal').value);
    const rate = parseFloat(document.getElementById('emiRate').value);
    const tenure = parseInt(document.getElementById('emiTenure').value);
    
    if (!principal || !rate || !tenure) {
        showNotification('Please fill all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                type: 'emi',
                principal: principal,
                rate: rate,
                tenure_months: tenure
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult('emiResult', data.result, [
                { label: 'EMI', value: `₹${data.result.emi.toFixed(2)}` },
                { label: 'Total Payment', value: `₹${data.result.total_payment.toFixed(2)}` },
                { label: 'Total Interest', value: `₹${data.result.total_interest.toFixed(2)}` }
            ]);
        } else {
            const errorMsg = data.error || 'Calculation failed';
            showNotification(errorMsg, 'error');
            console.error('EMI Calculation error:', data);
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Calculate error:', error);
    }
}

async function calculateSIP() {
    const amount = parseFloat(document.getElementById('sipAmount').value);
    const rate = parseFloat(document.getElementById('sipRate').value);
    const years = parseInt(document.getElementById('sipYears').value);
    
    if (!amount || !rate || !years) {
        showNotification('Please fill all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                type: 'sip',
                monthly_investment: amount,
                rate: rate,
                time_years: years
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult('sipResult', data.result, [
                { label: 'Total Invested', value: `₹${data.result.total_invested.toFixed(2)}` },
                { label: 'Maturity Amount', value: `₹${data.result.maturity_amount.toFixed(2)}` },
                { label: 'Gains', value: `₹${data.result.gains.toFixed(2)}` },
                { label: 'Return Percentage', value: `${data.result.return_percentage.toFixed(2)}%` }
            ]);
        } else {
            if (response.status === 401 || response.status === 422) {
                logout();
                showNotification('Session expired. Please login again.', 'error');
            } else {
                showNotification(data.error || 'Calculation failed', 'error');
            }
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Calculate error:', error);
    }
}

async function calculateCompound() {
    const principal = parseFloat(document.getElementById('compoundPrincipal').value);
    const rate = parseFloat(document.getElementById('compoundRate').value);
    const years = parseInt(document.getElementById('compoundYears').value);
    
    if (!principal || !rate || !years) {
        showNotification('Please fill all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                type: 'compound_interest',
                principal: principal,
                rate: rate,
                time_years: years
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult('compoundResult', data.result, [
                { label: 'Principal', value: `₹${data.result.principal.toFixed(2)}` },
                { label: 'Maturity Amount', value: `₹${data.result.maturity_amount.toFixed(2)}` },
                { label: 'Interest Earned', value: `₹${data.result.interest_earned.toFixed(2)}` }
            ]);
        } else {
            if (response.status === 401 || response.status === 422) {
                logout();
                showNotification('Session expired. Please login again.', 'error');
            } else {
                showNotification(data.error || 'Calculation failed', 'error');
            }
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Calculate error:', error);
    }
}

async function calculateSimple() {
    const principal = parseFloat(document.getElementById('simplePrincipal').value);
    const rate = parseFloat(document.getElementById('simpleRate').value);
    const years = parseInt(document.getElementById('simpleYears').value);
    
    if (!principal || !rate || !years) {
        showNotification('Please fill all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                type: 'simple_interest',
                principal: principal,
                rate: rate,
                time_years: years
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult('simpleResult', data.result, [
                { label: 'Principal', value: `₹${data.result.principal.toFixed(2)}` },
                { label: 'Total Amount', value: `₹${data.result.total_amount.toFixed(2)}` },
                { label: 'Interest Earned', value: `₹${data.result.interest.toFixed(2)}` }
            ]);
        } else {
            if (response.status === 401 || response.status === 422) {
                logout();
                showNotification('Session expired. Please login again.', 'error');
            } else {
                showNotification(data.error || 'Calculation failed', 'error');
            }
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Calculate error:', error);
    }
}

function displayResult(elementId, result, items) {
    const resultDiv = document.getElementById(elementId);
    resultDiv.innerHTML = '<h4>Calculation Results</h4>';
    
    items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'result-item';
        itemDiv.innerHTML = `
            <span class="result-label">${item.label}</span>
            <span class="result-value">${item.value}</span>
        `;
        resultDiv.appendChild(itemDiv);
    });
    
    resultDiv.classList.add('show');
}

// Market Updates
async function showMarketUpdates() {
    document.getElementById('chatSection').style.display = 'none';
    document.getElementById('calculatorSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'none';
    document.getElementById('marketSection').style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/market-updates`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayMarketUpdates(data);
        } else {
            if (response.status === 401 || response.status === 422) {
                logout();
                showNotification('Session expired. Please login again.', 'error');
            } else {
                showNotification('Error loading market updates', 'error');
            }
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('Market updates error:', error);
    }
}

function displayMarketUpdates(data) {
    const content = document.getElementById('marketContent');
    let html = '';
    
    // Market Indices
    if (data.indices) {
        html += '<div class="market-card"><h3>Market Indices</h3>';
        for (const [name, value] of Object.entries(data.indices)) {
            const changeClass = value.change >= 0 ? 'positive' : 'negative';
            html += `
                <div class="market-index">
                    <div>
                        <div class="index-name">${name}</div>
                        <div class="index-value">${value.value.toLocaleString()}</div>
                    </div>
                    <div class="index-change ${changeClass}">
                        ${value.change >= 0 ? '+' : ''}${value.change.toFixed(2)} 
                        (${value.change_percent >= 0 ? '+' : ''}${value.change_percent.toFixed(2)}%)
                    </div>
                </div>
            `;
        }
        html += '</div>';
    }
    
    // Top Stocks
    if (data.top_stocks && data.top_stocks.length > 0) {
        html += '<div class="market-card"><h3>Top Stocks</h3>';
        data.top_stocks.forEach(stock => {
            const changeClass = stock.change >= 0 ? 'positive' : 'negative';
            html += `
                <div class="market-index">
                    <div>
                        <div class="index-name">${stock.symbol}</div>
                        <div class="index-value">₹${stock.price.toFixed(2)}</div>
                    </div>
                    <div class="index-change ${changeClass}">
                        ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)} 
                        (${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%)
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Latest News
    if (data.latest_news && data.latest_news.length > 0) {
        html += '<div class="market-card"><h3>Latest Finance News</h3>';
        data.latest_news.forEach(news => {
            html += `
                <div class="history-item">
                    <div class="history-query">${news.title}</div>
                    <div class="history-response">${news.summary}</div>
                    <div class="history-time">${news.source} - ${news.date}</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    content.innerHTML = html;
}

function closeMarketUpdates() {
    document.getElementById('marketSection').style.display = 'none';
    document.getElementById('chatSection').style.display = 'block';
}

// History
async function showHistory() {
    document.getElementById('chatSection').style.display = 'none';
    document.getElementById('calculatorSection').style.display = 'none';
    document.getElementById('marketSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/history`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayHistory(data.history);
        } else {
            if (response.status === 401 || response.status === 422) {
                logout();
                showNotification('Session expired. Please login again.', 'error');
            } else {
                showNotification('Error loading history', 'error');
            }
        }
    } catch (error) {
        showNotification('Error connecting to server', 'error');
        console.error('History error:', error);
    }
}

function displayHistory(history) {
    const content = document.getElementById('historyContent');
    
    if (!history || history.length === 0) {
        content.innerHTML = '<p>No conversation history yet. Start chatting to see your history here!</p>';
        return;
    }
    
    let html = '';
    history.forEach(item => {
        const date = new Date(item.timestamp);
        html += `
            <div class="history-item">
                <div class="history-query">${item.query}</div>
                <div class="history-response">${formatMessage(item.response)}</div>
                <div class="history-time">${date.toLocaleString()}</div>
            </div>
        `;
    });
    
    content.innerHTML = html;
}

function closeHistory() {
    document.getElementById('historySection').style.display = 'none';
    document.getElementById('chatSection').style.display = 'block';
}

// Motivational Quote
async function getMotivationalQuote() {
    try {
        const response = await fetch(`${API_BASE_URL}/quote`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessageToChat(data.quote, 'bot');
        }
    } catch (error) {
        console.error('Quote error:', error);
    }
}

// Notification System
function showNotification(message, type = 'info') {
    // Simple notification - you can enhance this with a toast library
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#2563eb'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Language Functions
async function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('preferredLanguage', lang);
    
    try {
        const response = await fetch(`${API_BASE_URL}/user/language`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: lang })
        });
        
        if (response.ok) {
            showNotification('Language preference updated', 'success');
        }
    } catch (error) {
        console.error('Error updating language:', error);
    }
}

// Combined handler for language selector in the UI
// Called from the <select onchange="changeLanguageAndUI(this.value)">
// Updates UI immediately and persists preference; updates backend only when logged in
function changeLanguageAndUI(lang) {
    try {
        // Update UI strings immediately
        if (typeof translateUI === 'function') {
            translateUI(lang);
        }

        // Persist preference locally
        localStorage.setItem('preferredLanguage', lang);

        // If user is logged in, notify backend about the preference
        if (accessToken) {
            // Fire-and-forget; changeLanguage will attempt server update
            changeLanguage(lang);
        } else {
            // Save UI-specific key as well for older codepaths
            localStorage.setItem('uiLanguage', lang);
            showNotification && showNotification('Language changed', 'info');
        }

        // Make sure selector shows current value
        const langSelector = document.getElementById('languageSelector');
        if (langSelector) langSelector.value = lang;
    } catch (err) {
        console.error('Error switching language:', err);
    }
}

// Text-to-Speech Functions
function speakText(text) {
    if (!synth || voiceResponseEnabled === false) return;
    
    // Stop any ongoing speech
    synth.cancel();
    
    // Clean text (remove markdown)
    const cleanText = text.replace(/\*\*/g, '').replace(/\*/g, '').replace(/•/g, '').replace(/\n/g, '. ');
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = currentLanguage === 'hi' ? 'hi-IN' : currentLanguage === 'te' ? 'te-IN' : 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    synth.speak(utterance);
}

function toggleVoiceResponse() {
    voiceResponseEnabled = !voiceResponseEnabled;
    localStorage.setItem('voiceResponse', voiceResponseEnabled.toString());
    
    const btn = document.getElementById('voiceToggleBtn');
    if (voiceResponseEnabled) {
        btn.classList.add('active');
        btn.title = 'Voice Response: ON (Click to turn off)';
        showNotification('Voice response enabled', 'success');
    } else {
        btn.classList.remove('active');
        btn.title = 'Voice Response: OFF (Click to turn on)';
        synth.cancel();
        showNotification('Voice response disabled', 'info');
    }
}

// Initialize voice response state
if (voiceResponseEnabled) {
    setTimeout(() => {
        const btn = document.getElementById('voiceToggleBtn');
        if (btn) {
            btn.classList.add('active');
            btn.title = 'Voice Response: ON (Click to turn off)';
        }
    }, 100);
}

// Quick Action Functions
function sendQuickMessage(message) {
    document.getElementById('chatInput').value = message;
    sendMessage();
    
    // Hide quick actions after selection
    const quickActions = document.getElementById('quickActions');
    if (quickActions) {
        quickActions.style.display = 'none';
    }
}

// Show quick actions again when input is focused
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('focus', () => {
                const quickActions = document.getElementById('quickActions');
                if (quickActions && chatInput.value === '') {
                    quickActions.style.display = 'flex';
                }
            });
            
            chatInput.addEventListener('input', () => {
                const quickActions = document.getElementById('quickActions');
                if (quickActions) {
                    if (chatInput.value === '') {
                        quickActions.style.display = 'flex';
                    } else {
                        quickActions.style.display = 'none';
                    }
                }
            });
        }
    }, 500);
});

// Export Chat History
async function exportChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/export-history`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Create download
            const blob = new Blob([data.export], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Chat history exported successfully!', 'success');
        } else {
            showNotification('Error exporting history', 'error');
        }
    } catch (error) {
        showNotification('Error exporting chat history', 'error');
        console.error('Export error:', error);
    }
}

// Live Charts Functions
let btcChart = null;
let goldChart = null;
let niftyChart = null;
let autoRefreshInterval = null;
let isAutoRefreshEnabled = false;

function showCharts() {
    document.getElementById('chatSection').style.display = 'none';
    document.getElementById('calculatorSection').style.display = 'none';
    document.getElementById('marketSection').style.display = 'none';
    document.getElementById('historySection').style.display = 'none';
    document.getElementById('chartsSection').style.display = 'block';
    
    // Initialize charts if not already initialized
    if (!btcChart) {
        initializeCharts();
    }
    
    // Load initial data
    updateChartsData();
    loadChartsNews();
}

function closeCharts() {
    document.getElementById('chartsSection').style.display = 'none';
    document.getElementById('chatSection').style.display = 'block';
    
    // Stop auto refresh if enabled
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function initializeCharts() {
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };

    // Bitcoin Chart
    const btcCtx = document.getElementById('bitcoinChart').getContext('2d');
    btcChart = new Chart(btcCtx, {
        ...chartConfig,
        data: {
            labels: [],
            datasets: [{
                label: 'Bitcoin (USD)',
                data: [],
                borderColor: '#f7931a',
                backgroundColor: 'rgba(247, 147, 26, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        }
    });

    // Gold Chart
    const goldCtx = document.getElementById('goldChart').getContext('2d');
    goldChart = new Chart(goldCtx, {
        ...chartConfig,
        data: {
            labels: [],
            datasets: [{
                label: 'Gold (USD/oz)',
                data: [],
                borderColor: '#ffd700',
                backgroundColor: 'rgba(255, 215, 0, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        }
    });

    // NIFTY 50 Chart
    const niftyCtx = document.getElementById('niftyChart').getContext('2d');
    niftyChart = new Chart(niftyCtx, {
        ...chartConfig,
        data: {
            labels: [],
            datasets: [{
                label: 'NIFTY 50',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        }
    });
}

async function updateChartsData() {
    try {
        // Generate sample data (in production, this would fetch from a real API)
        const now = Date.now();
        const labels = [];
        const btcData = [];
        const goldData = [];
        const niftyData = [];
        
        // Generate 30 data points for the last 30 hours
        for (let i = 29; i >= 0; i--) {
            const time = new Date(now - i * 60 * 60 * 1000);
            labels.push(time.getHours() + ':00');
            
            // Simulate price movements
            const btcBase = 45000 + Math.random() * 2000;
            const goldBase = 2000 + Math.random() * 50;
            const niftyBase = 21000 + Math.random() * 500;
            
            btcData.push(btcBase);
            goldData.push(goldBase);
            niftyData.push(niftyBase);
        }
        
        // Update charts
        btcChart.data.labels = labels;
        btcChart.data.datasets[0].data = btcData;
        btcChart.update();
        
        goldChart.data.labels = labels;
        goldChart.data.datasets[0].data = goldData;
        goldChart.update();
        
        niftyChart.data.labels = labels;
        niftyChart.data.datasets[0].data = niftyData;
        niftyChart.update();
        
        // Update price displays
        const btcCurrent = btcData[btcData.length - 1];
        const btcPrev = btcData[btcData.length - 2];
        const btcChange = btcCurrent - btcPrev;
        const btcChangePercent = (btcChange / btcPrev) * 100;
        
        document.querySelector('#btcPrice .price-value').textContent = `$${btcCurrent.toFixed(2)}`;
        const btcChangeEl = document.getElementById('btcChange');
        btcChangeEl.textContent = `${btcChange >= 0 ? '+' : ''}${btcChange.toFixed(2)} (${btcChangePercent >= 0 ? '+' : ''}${btcChangePercent.toFixed(2)}%)`;
        btcChangeEl.className = `price-change ${btcChange >= 0 ? 'positive' : 'negative'}`;
        
        const goldCurrent = goldData[goldData.length - 1];
        const goldPrev = goldData[goldData.length - 2];
        const goldChange = goldCurrent - goldPrev;
        const goldChangePercent = (goldChange / goldPrev) * 100;
        
        document.querySelector('#goldPrice .price-value').textContent = `$${goldCurrent.toFixed(2)}`;
        const goldChangeEl = document.getElementById('goldChange');
        goldChangeEl.textContent = `${goldChange >= 0 ? '+' : ''}${goldChange.toFixed(2)} (${goldChangePercent >= 0 ? '+' : ''}${goldChangePercent.toFixed(2)}%)`;
        goldChangeEl.className = `price-change ${goldChange >= 0 ? 'positive' : 'negative'}`;
        
        const niftyCurrent = niftyData[niftyData.length - 1];
        const niftyPrev = niftyData[niftyData.length - 2];
        const niftyChange = niftyCurrent - niftyPrev;
        const niftyChangePercent = (niftyChange / niftyPrev) * 100;
        
        document.querySelector('#niftyPrice .price-value').textContent = niftyCurrent.toFixed(2);
        const niftyChangeEl = document.getElementById('niftyChange');
        niftyChangeEl.textContent = `${niftyChange >= 0 ? '+' : ''}${niftyChange.toFixed(2)} (${niftyChangePercent >= 0 ? '+' : ''}${niftyChangePercent.toFixed(2)}%)`;
        niftyChangeEl.className = `price-change ${niftyChange >= 0 ? 'positive' : 'negative'}`;
        
    } catch (error) {
        console.error('Error updating charts:', error);
        showNotification('Error updating chart data', 'error');
    }
}

async function loadChartsNews() {
    try {
        const response = await fetch(`${API_BASE_URL}/news`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.news) {
            displayChartsNews(data.news);
        }
    } catch (error) {
        console.error('Error loading news:', error);
    }
}

function displayChartsNews(news) {
    const newsContent = document.getElementById('newsContent');
    if (!news || news.length === 0) {
        newsContent.innerHTML = '<p>No news available at the moment.</p>';
        return;
    }
    
    let html = '';
    news.slice(0, 5).forEach(item => {
        html += `
            <div class="news-item">
                <div class="news-title">${item.title}</div>
                <div class="news-summary">${item.summary}</div>
                <div class="news-meta">${item.source} - ${item.date}</div>
            </div>
        `;
    });
    
    newsContent.innerHTML = html;
}

function toggleAutoRefresh() {
    isAutoRefreshEnabled = !isAutoRefreshEnabled;
    const btn = document.getElementById('autoRefreshBtn');
    
    if (isAutoRefreshEnabled) {
        btn.classList.add('active');
        btn.title = 'Auto Refresh: ON';
        showNotification('Auto refresh enabled (every 30 seconds)', 'success');
        
        // Refresh every 30 seconds
        autoRefreshInterval = setInterval(() => {
            updateChartsData();
        }, 30000);
    } else {
        btn.classList.remove('active');
        btn.title = 'Auto Refresh: OFF';
        showNotification('Auto refresh disabled', 'info');
        
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    }
}

// Guest Mode Functions
function continueAsGuest() {
    // Hide login modal and show main container
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('mainContainer').style.display = 'block';
    
    // Show guest banner
    const guestBanner = document.getElementById('guestBanner');
    if (guestBanner) {
        guestBanner.style.display = 'flex';
    }
    
    // Clear any stored token
    accessToken = null;
    localStorage.removeItem('accessToken');
    
    showNotification('Welcome! You are browsing as a guest.', 'info');
}

function closeGuestBanner() {
    const guestBanner = document.getElementById('guestBanner');
    if (guestBanner) {
        guestBanner.style.display = 'none';
    }
}

