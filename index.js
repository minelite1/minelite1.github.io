function showDialog() {
    document.getElementById("request").showModal();
}

const links = {
    'donation-alerts': 'https://www.donationalerts.com/r/sevenrp',
    discord: 'https://discord.gg/teJQfYK6UJ'
}

function redirect(name) {
    window.location.href = links[name];
}

async function sendToApi() {
    let data = {};
    document.querySelectorAll("input,textarea").forEach((input) => {
        if(input.value === '') {return;}
        data[input.id] = input.value;
    })
    const res = await fetch("/send", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    if(res.status === 200) {
        sendMessage('Успешно', 'Заявка успешно отправлена!')
    } else {
        sendMessage('Ошибка', 'Проверьте, правильно ли вы заполнили все поля.')
    }
}

function sendMessage(title, description) {
    document.querySelector(".message__title").innerHTML = title
    document.querySelector(".message__description").innerHTML = description
    document.getElementById("message").showModal();
}

document.getElementById("send").addEventListener("click", async (ev) => {
    sendToApi()
})