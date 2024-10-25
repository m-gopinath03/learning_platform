document.addEventListener('DOMContentLoaded', function() {
    const contentList = document.getElementById('content-list');
    if (contentList) {
        new Sortable(contentList, {
            animation: 150,
            onEnd: function() {
                const newOrder = Array.from(contentList.children).map(item => item.dataset.id);
                
                // Send new order to server
                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: 'new_order=' + newOrder.join(',')
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showToast('Content order updated successfully');
                    }
                });
            }
        });
    }
});

// Helper function to get CSRF token
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
