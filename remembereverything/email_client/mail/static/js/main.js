// Основные функции для всех страниц
document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений через 3 секунды
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 300);
        }, 3000);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить это письмо?')) {
                e.preventDefault();
            }
        });
    });
});

// Функция для форматирования даты
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return 'Сегодня в ' + date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
    } else if (diffDays === 1) {
        return 'Вчера в ' + date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
    } else if (diffDays < 7) {
        return diffDays + ' дня назад';
    } else {
        return date.toLocaleDateString('ru-RU');
    }
}

// Функция для поиска писем
function searchEmails(query) {
    const rows = document.querySelectorAll('.email-row');
    query = query.toLowerCase();
    
    rows.forEach(function(row) {
        const sender = row.querySelector('.sender')?.textContent.toLowerCase() || '';
        const subject = row.querySelector('.subject')?.textContent.toLowerCase() || '';
        
        if (sender.includes(query) || subject.includes(query)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}