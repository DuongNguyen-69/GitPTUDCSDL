document.addEventListener('DOMContentLoaded', function() {
    const puzzleText = document.getElementById('puzzleText');
    const guessInput = document.getElementById('guessInput');
    const guessButton = document.getElementById('guessButton');
    const playerResults = document.getElementById('playerResults');
    const newGameButton = document.getElementById('newGameButton');
    const remainingAttemptsText = document.getElementById('remainingAttempts');
    const puzzleCategory = document.getElementById('puzzleCategory');
    const resultMessage = document.getElementById('resultMessage');
    
    // List of puzzles with categories
    const puzzles = [
        { text: "XIN CHÀO", category: "Lời chào" },
        { text: "CẢM ƠN BẠN", category: "Lời cảm ơn" },
        { text: "VIỆT NAM", category: "Quốc gia" },
        { text: "PHỞ BÒ", category: "Món ăn" },
        { text: "HÀ NỘI", category: "Thành phố" },
        { text: "BÁNH CHƯNG", category: "Món ăn truyền thống" },
        { text: "ÁO DÀI", category: "Trang phục" },
        { text: "CÀ PHÊ SỮA ĐÁ", category: "Đồ uống" },
        { text: "ĐỒNG BẰNG SÔNG CỬU LONG", category: "Địa lý" },
        { text: "TẾT NGUYÊN ĐÁN", category: "Ngày lễ" }
    ];
    
    let currentPuzzle = null;
    let displayedPuzzle = '';
    let score = 0;
    let remainingAttempts = 5;
    let guessedLetters = [];
    let gameActive = true;
    
    // Initialize new game
    function startNewGame() {
        resultMessage.textContent = '';
        resultMessage.classList.remove('text-success', 'text-danger');
        // Choose a random puzzle
        currentPuzzle = puzzles[Math.floor(Math.random() * puzzles.length)];
        
        // Reset game state
        guessedLetters = [];
        score = 0;
        remainingAttempts = 5;
        gameActive = true;
        
        // Update display
        updatePuzzleDisplay();
        puzzleCategory.textContent = currentPuzzle.category;
        remainingAttemptsText.textContent = remainingAttempts;
        
        // Enable controls
        guessInput.disabled = false;
        guessButton.disabled = false;
        document.getElementById('spinButton').disabled = false;
        
        // Clear input
        guessInput.value = '';
        
        // Allow focusing on guess input
        guessInput.focus();
    }
    
    function updatePuzzleDisplay() {
        displayedPuzzle = currentPuzzle.text.split('').map(char => {
            if (char === ' ') return ' ';
            return guessedLetters.includes(char) ? char : '_';
        }).join(' ');
        
        puzzleText.textContent = displayedPuzzle;
    }
    
    // Handle spinning the wheel
    window.handleSpin = function(points) {
        if (!gameActive) return;
        
        if (points === 'bankrupt') {
            score = 0;
            showMessage(`Bạn bị mất điểm!`, 'text-danger');
        } else {
            score += points;
            showMessage(`Bạn quay được ${points} điểm!`, 'text-success');
        }
    };
    
    function showMessage(message, className) {
        resultMessage.textContent = message;
        resultMessage.className = '';
        if (className) {
            resultMessage.classList.add(className);
        }
    }
    
    // Handle letter guessing
    guessButton.addEventListener('click', handleGuess);
    guessInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            handleGuess();
        }
    });
    
    function handleGuess() {
        if (!gameActive) return;
        
        const guess = guessInput.value.trim().toUpperCase();
        
        // Validate input
        if (!guess) {
            showMessage('Vui lòng nhập một chữ cái!', 'text-danger');
            return;
        }
        
        if (guess.length > 1) {
            showMessage('Vui lòng chỉ nhập một chữ cái!', 'text-danger');
            return;
        }
        
        if (guessedLetters.includes(guess)) {
            showMessage(`Bạn đã đoán chữ cái ${guess} rồi!`, 'text-warning');
            guessInput.value = '';
            return;
        }
        
        // Add to guessed letters
        guessedLetters.push(guess);
        
        // Check if guess is correct
        if (currentPuzzle.text.includes(guess)) {
            updatePuzzleDisplay();
            showMessage(`Đúng rồi! Chữ ${guess} có trong ô chữ.`, 'text-success');
            
            // Check if puzzle is solved
            if (!displayedPuzzle.includes('_')) {
                gameActive = false;
                showMessage(`Chúc mừng! Bạn đã giải được ô chữ và đạt ${score} điểm!`, 'text-success');
                submitScore(score);
                guessInput.disabled = true;
                guessButton.disabled = true;
                document.getElementById('spinButton').disabled = true;
            }
        } else {
            remainingAttempts--;
            remainingAttemptsText.textContent = remainingAttempts;
            showMessage(`Sai rồi! Chữ ${guess} không có trong ô chữ.`, 'text-danger');
            
            // Check if game over
            if (remainingAttempts <= 0) {
                gameActive = false;
                showMessage(`Bạn đã hết lượt chơi! Đáp án đúng là: ${currentPuzzle.text}`, 'text-danger');
                submitScore(score);
                puzzleText.textContent = currentPuzzle.text;
                guessInput.disabled = true;
                guessButton.disabled = true;
                document.getElementById('spinButton').disabled = true;
            }
        }
        
        // Clear input
        guessInput.value = '';
        guessInput.focus();
    }
    
    function submitScore(score) {
        // Get player name or use default
        const playerName = prompt('Nhập tên của bạn:', 'Người chơi');
        const player = playerName || 'Người chơi ' + Date.now();
        
        fetch('/submit-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player, score })
        })
        .then(response => response.json())
        .then(data => updateScoreboard(data))
        .catch(error => console.error('Lỗi:', error));
    }
    
    function updateScoreboard(scores) {
        playerResults.innerHTML = '';
        // Sort by score (highest first)
        scores.sort((a, b) => b.score - a.score);
        
        // Create table headers
        const table = document.createElement('table');
        table.className = 'table table-striped table-dark';
        
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        const rankHeader = document.createElement('th');
        rankHeader.textContent = 'Hạng';
        headerRow.appendChild(rankHeader);
        
        const nameHeader = document.createElement('th');
        nameHeader.textContent = 'Người chơi';
        headerRow.appendChild(nameHeader);
        
        const scoreHeader = document.createElement('th');
        scoreHeader.textContent = 'Điểm';
        headerRow.appendChild(scoreHeader);
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        scores.forEach((result, index) => {
            const row = document.createElement('tr');
            
            const rankCell = document.createElement('td');
            rankCell.textContent = index + 1;
            row.appendChild(rankCell);
            
            const nameCell = document.createElement('td');
            nameCell.textContent = result.player;
            row.appendChild(nameCell);
            
            const scoreCell = document.createElement('td');
            scoreCell.textContent = result.score;
            row.appendChild(scoreCell);
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        playerResults.appendChild(table);
    }
    
    // Start new game when button is clicked
    newGameButton.addEventListener('click', startNewGame);
    
    // Load scores when page loads
    fetch('/scores')
        .then(response => response.json())
        .then(data => updateScoreboard(data));
    
    // Start the first game
    startNewGame();
});
