// Основные функции
document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 300);
        }, 3000);
    });
});

// Функция для перемещения письма
function moveEmail(emailId, folder) {
    fetch(`/api/email/${emailId}/move/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({folder: folder})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const row = document.querySelector(`tr[data-email-id="${emailId}"]`);
            if (row) row.remove();
            showMessage('Письмо перемещено', 'success');
        }
    });
}

// Функция для удаления письма
function deletePermanently(emailId) {
    if (confirm('Удалить письмо навсегда?')) {
        fetch(`/api/email/${emailId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const row = document.querySelector(`tr[data-email-id="${emailId}"]`);
                if (row) row.remove();
                showMessage('Письмо удалено', 'success');
            }
        });
    }
}

// Вспомогательная функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для показа сообщений
function showMessage(text, type) {
    const messagesDiv = document.querySelector('.messages');
    if (messagesDiv) {
        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.textContent = text;
        messagesDiv.appendChild(message);
        
        setTimeout(() => {
            message.remove();
        }, 3000);
    }
}
