// Récupérer la liste des salons uniques
async function getRooms() {
    const db = await initDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([storeName], "readonly");
        const store = transaction.objectStore(storeName);
        const request = store.getAll();

        request.onsuccess = () => {
            const messages = request.result;
            const rooms = [...new Set(messages.map(msg => msg.roomSlug))];
            resolve(rooms);
        };
        request.onerror = () => reject(request.error);
    });
}

// Afficher tous les messages par salon
async function displayAllMessages() {
    const rooms = await getRooms();
    const messagesDiv = document.getElementById("all-messages");
    let html = '<h2>Mes Messages</h2>';
    for (const roomSlug of rooms) {
        const messages = await getMessages(roomSlug);
        html += `<h3>Salon: ${roomSlug}</h3>`;
        html += messages.map(msg => 
            `<p><b>${msg.username}</b>: ${msg.content} <small>${new Date(msg.timestamp).toLocaleString()}</small></p>`
        ).join("");
        html += '<hr>';
    }
    messagesDiv.innerHTML = html;
}