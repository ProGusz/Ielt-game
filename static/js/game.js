let currentWord = '';
let player = {};
let enemy = {};

function signup() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username, password: password}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Signup successful! Please login.');
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during signup. Please try again.');
    });
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username, password: password}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('start-screen').style.display = 'block';
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during login. Please try again.');
    });
}

function logout() {
    fetch('/logout', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('auth-screen').style.display = 'block';
            document.getElementById('start-screen').style.display = 'none';
            document.getElementById('game-screen').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during logout. Please try again.');
    });
}

function startGame() {
    const difficulty = document.getElementById('difficulty-select').value;
    fetch('/start_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({difficulty: difficulty}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success === false) {
            alert(data.message);
            return;
        }
        player = data;
        document.getElementById('start-screen').style.display = 'none';
        document.getElementById('game-screen').style.display = 'block';
        updatePlayerStats();
        getNewWord();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while starting the game. Please try again.');
    });
}

function getNewWord() {
    fetch('/get_word')
        .then(response => response.json())
        .then(data => {
            if (data.success === false) {
                alert(data.message);
                return;
            }
            currentWord = data.word;
            document.getElementById('definition').textContent = data.definition;
            displayWordOptions(data.options);
            document.getElementById('result').textContent = '';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while getting a new word. Please try again.');
        });
}

function displayWordOptions(options) {
    const wordOptionsContainer = document.getElementById('word-options');
    wordOptionsContainer.innerHTML = '';
    options.forEach(word => {
        const button = document.createElement('button');
        button.textContent = word;
        button.className = 'word-option';
        button.onclick = () => checkAnswer(word);
        wordOptionsContainer.appendChild(button);
    });
}

function checkAnswer(selectedWord) {
    fetch('/check_answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({word: selectedWord, correct_word: currentWord}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success === false) {
            alert(data.message);
            return;
        }
        if (data.is_correct) {
            document.getElementById('result').textContent = 'Correct! You dealt damage to the enemy!';
        } else {
            document.getElementById('result').textContent = `Incorrect. The correct word was "${currentWord}". You took damage!`;
        }
        player = data.player;
        enemy = data.enemy;
        updatePlayerStats();
        updateEnemyStats();
        if (data.enemy_defeated) {
            alert('Enemy defeated! A new enemy appears!');
        }
        if (data.game_over) {
            alert('Game Over! Your health reached 0.');
            document.getElementById('start-screen').style.display = 'block';
            document.getElementById('game-screen').style.display = 'none';
        } else {
            setTimeout(getNewWord, 1500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while checking the answer. Please try again.');
    });
}

function updatePlayerStats() {
    document.getElementById('player-level').textContent = player.level;
    document.getElementById('player-exp').textContent = player.exp;
    const healthPercentage = (player.health / player.max_health) * 100;
    document.getElementById('player-health-bar').style.width = `${healthPercentage}%`;
}

function updateEnemyStats() {
    document.getElementById('enemy-name').textContent = enemy.name;
    const healthPercentage = (enemy.health / enemy.max_health) * 100;
    document.getElementById('enemy-health-bar').style.width = `${healthPercentage}%`;
}

// Event listeners for buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('button[onclick="login()"]').addEventListener('click', login);
    document.querySelector('button[onclick="signup()"]').addEventListener('click', signup);
    document.querySelector('button[onclick="startGame()"]').addEventListener('click', startGame);
    document.querySelector('button[onclick="logout()"]').addEventListener('click', logout);
});