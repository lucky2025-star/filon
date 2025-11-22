// Dashboard JS logic
// Use current hostname instead of localhost
const API_BASE = window.location.origin;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        button.classList.add('active');
        document.getElementById(button.dataset.tab).classList.add('active');
        
        // Load credential status when Settings tab is clicked
        if (button.dataset.tab === 'settings') {
            loadCredentialStatus();
        }
    });
});

// Load credential status on page load and periodically
window.addEventListener('load', () => {
    loadCredentialStatus();
    // Refresh every 5 seconds
    setInterval(loadCredentialStatus, 5000);
});

// Load and display credential status with masked hashes
async function loadCredentialStatus() {
    try {
        const response = await fetch(`${API_BASE}/check-credentials`);
        const data = await response.json();
        
        if (data.status === 'success' && data.credentials) {
            const credentials = data.credentials;
            
            for (const [exchange, creds] of Object.entries(credentials)) {
                // Find input fields for this exchange
                const apiKeyInput = document.querySelector(`[data-exchange="${exchange}"][data-type="api_key"]`);
                const apiSecretInput = document.querySelector(`[data-exchange="${exchange}"][data-type="api_secret"]`);
                const passwordInput = document.querySelector(`[data-exchange="${exchange}"][data-type="password"]`);
                
                // Display masked credentials in placeholders and add visual indicator
                if (apiKeyInput && creds.has_api_key) {
                    apiKeyInput.placeholder = `🔐 ${creds.api_key_masked}`;
                    apiKeyInput.value = '';
                    apiKeyInput.classList.add('has-credentials');
                }
                
                if (apiSecretInput && creds.has_api_secret) {
                    apiSecretInput.placeholder = `🔐 ${creds.api_secret_masked}`;
                    apiSecretInput.value = '';
                    apiSecretInput.classList.add('has-credentials');
                }
                
                if (passwordInput && creds.has_password) {
                    passwordInput.placeholder = `🔐 ${creds.password_masked}`;
                    passwordInput.value = '';
                    passwordInput.classList.add('has-credentials');
                }
            }
        }
    } catch (error) {
        console.error('Error loading credential status:', error);
    }
}

// Save credentials with encryption
async function saveCredentials() {
    const saveBtn = document.getElementById('save-credentials');
    const originalText = saveBtn.textContent;
    
    const credentials = {};
    const inputs = document.querySelectorAll('.exchange-input');
    
    inputs.forEach(input => {
        const exchange = input.dataset.exchange;
        const type = input.dataset.type;
        const value = input.value;
        
        if (value && value.trim()) {
            const key = `${exchange}_${type}`;
            credentials[key] = value;
        }
    });
    
    if (Object.keys(credentials).length === 0) {
        showCredentialStatus('⚠️ Please enter at least one credential', 'error');
        return;
    }
    
    try {
        // Step 1: Validate credentials
        saveBtn.textContent = '🔍 Validating...';
        saveBtn.disabled = true;
        showCredentialStatus('🔍 Validating credentials with exchanges...', 'info');
        
        console.log('Validating credentials...');
        const validateResponse = await fetch(`${API_BASE}/validate-credentials`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials)
        });
        
        const validateData = await validateResponse.json();
        console.log('Validation results:', validateData);
        
        if (validateData.status === 'success' && validateData.results) {
            const results = validateData.results;
            let allValid = true;
            let validationMessage = '';
            
            for (const [exchange, result] of Object.entries(results)) {
                if (!result.valid) {
                    allValid = false;
                    validationMessage += `❌ ${exchange}: ${result.message}\n`;
                } else {
                    validationMessage += `✅ ${exchange}: ${result.message}\n`;
                }
            }
            
            // Show validation results
            showCredentialStatus(validationMessage, allValid ? 'success' : 'error');
            
            if (!allValid) {
                console.warn('Validation failed:', validationMessage);
                saveBtn.textContent = originalText;
                saveBtn.disabled = false;
                return;
            }
            
            // Step 2: Save valid credentials
            saveBtn.textContent = '⏳ Saving...';
            showCredentialStatus('✅ All credentials valid! Saving...', 'success');
            
            console.log('Sending credentials to:', `${API_BASE}/save-credentials`);
            const response = await fetch(`${API_BASE}/save-credentials`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });
            
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (response.ok && data.status === 'success') {
                showCredentialStatus('✅ ' + data.message + '\n🔒 Credentials encrypted and saved!', 'success');
                // Clear the form
                document.querySelectorAll('.exchange-input').forEach(input => input.value = '');
                setTimeout(() => showCredentialStatus('', ''), 5000);
            } else {
                showCredentialStatus('❌ ' + (data.message || 'Error saving credentials'), 'error');
            }
        } else {
            showCredentialStatus('❌ ' + (validateData.message || 'Validation error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showCredentialStatus('❌ Connection error: ' + error.message, 'error');
    } finally {
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    }
}

function showCredentialStatus(message, type) {
    const statusEl = document.getElementById('credential-status');
    if (!statusEl) return;
    
    statusEl.textContent = message;
    statusEl.className = 'credential-status ' + type;
}

// Delete credentials for an exchange
async function deleteCredentials(exchange) {
    if (!confirm(`Delete ${exchange.toUpperCase()} credentials? This cannot be undone.`)) {
        return;
    }
    
    try {
        showCredentialStatus(`🗑️ Deleting ${exchange} credentials...`, 'info');
        
        const response = await fetch(`${API_BASE}/delete-credentials`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ exchange: exchange })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // Clear the form fields for this exchange
            document.querySelectorAll(`[data-exchange="${exchange}"]`).forEach(input => {
                input.value = '';
            });
            
            showCredentialStatus(`✅ ${exchange.toUpperCase()} credentials deleted successfully!`, 'success');
            setTimeout(() => showCredentialStatus('', ''), 3000);
        } else {
            showCredentialStatus('❌ ' + (data.message || 'Error deleting credentials'), 'error');
        }
    } catch (error) {
        console.error('Error deleting credentials:', error);
        showCredentialStatus('❌ Connection error: ' + error.message, 'error');
    }
}

// Fetch and display prices
async function fetchPrices() {
    try {
        // Fetch prices with proper symbol format
        const response = await fetch(`${API_BASE}/prices/BTC/USDT,ETH/USDT`);
        if (!response.ok) {
            console.error(`Prices API error: ${response.status}`);
            displayPrices({ prices: {}, configured_exchanges: [] });
            return;
        }
        const data = await response.json();
        displayPrices(data);
    } catch (error) {
        console.error('Error fetching prices:', error);
        displayPrices({ prices: {}, configured_exchanges: [] });
    }
}

function displayPrices(data) {
    const tbody = document.getElementById('price-tbody');
    tbody.innerHTML = '';
    
    // Check if we have the new response format
    const prices = data.prices || data;
    const configured = data.configured_exchanges || [];
    const message = data.message || '';
    
    // If no exchanges configured, show message
    if (!configured || configured.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: #666;">
                    <strong>⚠️ No exchanges configured</strong><br>
                    <small>Add your API credentials in the Settings tab to see live prices</small>
                </td>
            </tr>
        `;
        return;
    }
    
    // If no price data, show explanation
    if (!prices || Object.keys(prices).length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: #666;">
                    <strong>Loading prices...</strong><br>
                    <small>${message || 'Fetching from ' + configured.length + ' exchanges'}</small>
                </td>
            </tr>
        `;
        return;
    }
    
    // Display prices
    for (const [symbol, exchanges] of Object.entries(prices)) {
        for (const [exchange, data] of Object.entries(exchanges)) {
            const row = document.createElement('tr');
            const bid = (data.bid || 0).toFixed(2);
            const ask = (data.ask || 0).toFixed(2);
            const last = (data.last || 0).toFixed(2);
            const spread = bid && ask ? (((ask - bid) / bid) * 100).toFixed(3) : 'N/A';
            
            row.innerHTML = `
                <td>${exchange.toUpperCase()}</td>
                <td>${bid === '0.00' ? '-' : bid}</td>
                <td>${ask === '0.00' ? '-' : ask}</td>
                <td>${last === '0.00' ? '-' : last}</td>
                <td class="spread-positive">${spread}%</td>
            `;
            tbody.appendChild(row);
        }
    }
}

// Fetch and display opportunities
async function fetchOpportunities() {
    try {
        const response = await fetch(`${API_BASE}/opportunities`);
        const opportunities = await response.json();
        displayOpportunities(opportunities);
    } catch (error) {
        console.error('Error fetching opportunities:', error);
    }
}

function displayOpportunities(opportunities) {
    const tbody = document.getElementById('opportunities-tbody');
    tbody.innerHTML = '';
    
    if (opportunities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No opportunities detected</td></tr>';
        return;
    }
    
    opportunities.forEach(opp => {
        const row = document.createElement('tr');
        const spreadClass = opp.spread_pct > 0.5 ? 'spread-positive' : 'spread-negative';
        
        row.innerHTML = `
            <td>${opp.symbol}</td>
            <td>${opp.buy_exchange}</td>
            <td>${opp.sell_exchange}</td>
            <td>${opp.buy_price.toFixed(2)}</td>
            <td>${opp.sell_price.toFixed(2)}</td>
            <td class="${spreadClass}">${opp.spread_pct.toFixed(3)}%</td>
            <td><button class="action-btn" onclick="executeOpportunity('${opp.buy_exchange}', '${opp.sell_exchange}', '${opp.symbol}')">Trade</button></td>
        `;
        tbody.appendChild(row);
    });
}

// Fetch and display balances
async function fetchBalances() {
    try {
        const response = await fetch(`${API_BASE}/balances`);
        const balances = await response.json();
        displayBalances(balances);
    } catch (error) {
        console.error('Error fetching balances:', error);
    }
}

function displayBalances(balances) {
    const tbody = document.getElementById('balances-tbody');
    tbody.innerHTML = '';
    
    for (const [exchange, assets] of Object.entries(balances)) {
        for (const [asset, data] of Object.entries(assets)) {
            if (data.free > 0 || data.total > 0) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${exchange}</td>
                    <td>${asset}</td>
                    <td>${(data.free || 0).toFixed(8)}</td>
                    <td>${(data.used || 0).toFixed(8)}</td>
                    <td>${(data.total || 0).toFixed(8)}</td>
                `;
                tbody.appendChild(row);
            }
        }
    }
}

// Fetch and display trade history
async function fetchTrades() {
    try {
        const response = await fetch(`${API_BASE}/trades`);
        const trades = await response.json();
        displayTrades(trades);
    } catch (error) {
        console.error('Error fetching trades:', error);
    }
}

function displayTrades(trades) {
    const tbody = document.getElementById('trades-tbody');
    tbody.innerHTML = '';
    
    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No trades yet</td></tr>';
        return;
    }
    
    trades.forEach(trade => {
        const row = document.createElement('tr');
        const statusClass = trade.status === 'completed' ? 'spread-positive' : 'spread-negative';
        
        row.innerHTML = `
            <td>${new Date(trade.timestamp).toLocaleString()}</td>
            <td>${trade.symbol}</td>
            <td>${trade.buy_exchange}</td>
            <td>${trade.sell_exchange}</td>
            <td>${trade.quantity}</td>
            <td class="${statusClass}">${trade.status}</td>
            <td>${trade.pnl ? trade.pnl.toFixed(2) : 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Execute an opportunity
function executeOpportunity(buyEx, sellEx, symbol) {
    alert(`Executing trade: Buy ${symbol} on ${buyEx}, Sell on ${sellEx}`);
    // API call to execute trade
}

// Update status
function updateStatus() {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');
    
    fetch(`${API_BASE}/health`)
        .then(r => {
            indicator.style.color = '#27ae60';
            text.textContent = 'Connected';
        })
        .catch(() => {
            indicator.style.color = '#e74c3c';
            text.textContent = 'Disconnected';
        });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    fetchPrices();
    fetchOpportunities();
    fetchBalances();
    fetchTrades();
    
    // Add credential save listener
    const saveCredentialsBtn = document.getElementById('save-credentials');
    if (saveCredentialsBtn) {
        saveCredentialsBtn.addEventListener('click', saveCredentials);
    }
    
    // Add settings save listener
    const saveSettingsBtn = document.getElementById('save-settings');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', () => {
            alert('Settings saved!');
        });
    }
    
    // Refresh every 5 seconds
    setInterval(() => {
        fetchPrices();
        fetchOpportunities();
        fetchBalances();
        updateStatus();
    }, 5000);
});
