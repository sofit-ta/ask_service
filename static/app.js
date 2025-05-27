document.addEventListener("DOMContentLoaded", () => {
    setupLikeButtons();
    markUserVotes();
    setupCorrectAnswerToggle();
});

function setupCorrectAnswerToggle() {
    const checkboxes = document.querySelectorAll(".mark-correct");

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", async (e) => {
            const answerId = checkbox.dataset.answerId;

            const response = await fetch(`/mark-correct/${answerId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    is_correct: checkbox.checked ? 1 : 0
                })
            });

            if (!response.ok) {
                alert("Ошибка при установке правильного ответа");
                checkbox.checked = !checkbox.checked; // Откат
            }
        });
    });
}

function setupLikeButtons() {
    const buttons = document.querySelectorAll("button[data-id][data-type][data-value]");
    for (const button of buttons) {
        button.addEventListener("click", async (e) => {
            e.preventDefault();

            const id = button.dataset.id;
            const type = button.dataset.type;
            const value = parseInt(button.dataset.value);

            const response = await fetch("/like/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: new URLSearchParams({ id, type, value }),
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const counter = document.getElementById(`like-counter-${type}-${id}`);
                    const buttons = document.querySelectorAll(`button[data-id="${id}"][data-type="${type}"]`);

                    // Обновляем счётчик
                    if (counter) {
                        if (counter.tagName === 'INPUT') {
                            counter.value = data.likes_amount;
                        } else {
                            counter.textContent = data.likes_amount;
                        }
                    }

                    // Обновляем состояние кнопок
                    if (data.user_vote !== null) {
                        buttons.forEach(btn => btn.classList.remove('active'));
                        button.classList.add('active');
                    } else {
                        buttons.forEach(btn => btn.classList.remove('active'));
                    }
                }
            }
        });
    }
}
function markUserVotes() {
    if (!window.userVotes) return;

    const buttons = document.querySelectorAll("button[data-type][data-id][data-value]");

    for (const button of buttons) {
        const type = button.dataset.type;
        const id = button.dataset.id;
        const value = parseInt(button.dataset.value);
        const key = `${type}_${id}`;
        if (window.userVotes[key] === value) {
            button.classList.add('active');
        }
    }
}

// Получение CSRF токена
function getCookie(name) {
    const cookieValue = document.cookie.split("; ").find(row => row.startsWith(name + "="));
    return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : null;
}