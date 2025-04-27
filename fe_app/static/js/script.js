const bookSelect = document.getElementById('book-select');
const chapterSelect = document.getElementById('chapter-select');
const versesContainer = document.getElementById('verses-container');
const prevChapterBtn = document.getElementById('prev-chapter-btn');
const nextChapterBtn = document.getElementById('next-chapter-btn');

let selectedBookName = '';
let currentBookChapters = [];

// --- Elementos de la sección de Conversación con IA ---
const characterSelect = document.getElementById('character-select');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatArea = document.getElementById('chat-area');

// --- Historial de la conversación con IA ---
let conversationHistory = [];

const characters = [
    { id: 'papa_francisco', name: 'Papa Francisco' },
    { id: 'elena_g_white', name: 'Elena G. de White' },
    { id: 'agustin_hipona', name: 'Agustín de Hipona: El Pensador Fundacional' },
    { id: 'tomas_aquino', name: 'Tomás de Aquino: El Maestro de la Síntesis' },
    { id: 'martin_lutero', name: 'Martín Lutero: El Motor de la Reforma' },
];

function loadChapters(bookName, storedChapter) {
    chapterSelect.innerHTML = '<option value="" disabled selected>Selecciona un capítulo</option>';
    fetch(`http://127.0.0.1:5000/capitulos/${bookName}`)
        .then(response => response.json())
        .then(chapters => {
            currentBookChapters = chapters;
            chapters.forEach(chapter => {
                const option = document.createElement('option');
                option.value = chapter;
                option.textContent = chapter;
                chapterSelect.appendChild(option);
            });
            if (storedChapter) {
                chapterSelect.value = storedChapter;
                loadVerses(bookName, storedChapter);
            }
        });
}

function loadVerses(bookName, chapter) {
    versesContainer.innerHTML = '';
    fetch(`http://127.0.0.1:5000/versiculos/${bookName}/${chapter}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(verse => {
                const verseElement = document.createElement('p');
                const verseNumberSpan = document.createElement('span');
                verseNumberSpan.className = 'verse-number';
                verseNumberSpan.textContent = `${verse.verse}. `;

                verseElement.appendChild(verseNumberSpan);
                verseElement.appendChild(document.createTextNode(verse.text));
                versesContainer.appendChild(verseElement);
            });
            const chapterNavButtons = document.getElementById('chapter-nav-buttons');
            if (chapterNavButtons) {
                chapterNavButtons.style.display = 'block';
            }
            const currentChapter = parseInt(chapter);
            const currentChapterIndex = currentBookChapters.indexOf(currentChapter);
            prevChapterBtn.disabled = currentChapterIndex <= 0;
            nextChapterBtn.disabled = currentChapterIndex >= currentBookChapters.length - 1;
        });
}

function addMessageToChat(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');

    if (sender === 'user') {
        messageElement.classList.add('user-message');
        messageElement.innerHTML = `<p>${message}</p>`;
        conversationHistory.push({
            role: 'user',
            parts: [{ text: message }]
        });
    } else if (sender === 'ai') {
        messageElement.classList.add('ai-message');
        messageElement.innerHTML = `<p>${message}</p>`;
        conversationHistory.push({
            role: 'model',
            parts: [{ text: message }]
        });
    } else if (sender === 'system') {
        messageElement.classList.add('system-message');
        messageElement.innerHTML = `<p>${message}</p>`;
    }

    chatArea.appendChild(messageElement);
    chatArea.scrollTop = chatArea.scrollHeight;

    console.log('Historial actualizado:', conversationHistory);
}

async function sendMessage() {
    const message = userInput.value.trim();
    const selectedCharacter = characterSelect.value;

    if (!message) {
        addMessageToChat("Por favor, escribe tu pregunta.", 'system');
        return;
    }
    if (selectedCharacter === 'default') {
         addMessageToChat("Por favor, selecciona un personaje.", 'system');
         return;
    }

    console.log('Mensaje del usuario:', message);
    console.log('Personaje seleccionado:', selectedCharacter);
   
    addMessageToChat(message, 'user');
     userInput.value = '';
    userInput.focus();

    try {
        addMessageToChat("...", 'system');
             const response = await fetch('http://127.0.0.1:5000/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                character: selectedCharacter,
                history: conversationHistory
            })
        });

         const thinkingMessage = chatArea.querySelector('.system-message:last-child');
         if(thinkingMessage && thinkingMessage.textContent === "...") {
             chatArea.removeChild(thinkingMessage);
         }


        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
        }

        const data = await response.json();

        if (data.status === 'success' && data.ai_response) {
             addMessageToChat(data.ai_response, 'ai');
        } else {
             const errorMessage = data.message || "El backend no devolvió una respuesta válida de IA.";
             addMessageToChat(`Error: ${errorMessage}`, 'system');
        }

    } catch (error) {
        console.error('Error al enviar el mensaje al backend:', error);

         const thinkingMessage = chatArea.querySelector('.system-message:last-child');
         if(thinkingMessage && thinkingMessage.textContent === "...") {
             chatArea.removeChild(thinkingMessage);
         }

        addMessageToChat("Hubo un error al comunicarse con el servidor. Por favor, inténtalo de nuevo.", 'system');
    }
}

function populateCharacterSelect() {
    characterSelect.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = 'default';
    defaultOption.textContent = 'Selecciona un personaje';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    characterSelect.appendChild(defaultOption);

    characters.forEach(character => {
        const option = document.createElement('option');
        option.value = character.id;
        option.textContent = character.name;
        characterSelect.appendChild(option);
    });
}

fetch('http://127.0.0.1:5000/libros')
    .then(response => response.json())
    .then(data => {
        data.forEach(book => {
            const option = document.createElement('option');
            option.value = book.nombre;
            option.textContent = book.nombre;
            bookSelect.appendChild(option);
        });

        const lastReadBook = localStorage.getItem('lastReadBook');
        const lastReadChapter = localStorage.getItem('lastReadChapter');

        if (lastReadBook) {
            bookSelect.value = lastReadBook;
            selectedBookName = lastReadBook;
            loadChapters(lastReadBook, lastReadChapter);
        }
    });

bookSelect.addEventListener('change', function() {
    selectedBookName = this.value;
    console.log('Libro seleccionado:', selectedBookName);
    localStorage.setItem('lastReadBook', selectedBookName);
    localStorage.removeItem('lastReadChapter');
    loadChapters(selectedBookName);
});

chapterSelect.addEventListener('change', function() {
    const selectedChapter = this.value;
    console.log('Capítulo seleccionado:', selectedChapter);
    console.log('Libro seleccionado (stored):', selectedBookName);
    localStorage.setItem('lastReadChapter', selectedChapter);
    loadVerses(selectedBookName, selectedChapter);
});

nextChapterBtn.addEventListener('click', function() {
    const currentChapter = parseInt(chapterSelect.value);
    const currentChapterIndex = currentBookChapters.indexOf(currentChapter);
    if (currentChapterIndex < currentBookChapters.length - 1) {
        const nextChapter = currentBookChapters[currentChapterIndex + 1];
        chapterSelect.value = nextChapter;
        loadVerses(selectedBookName, nextChapter);
    } else {
        console.log('Estás en el último capítulo.');
    }
});

prevChapterBtn.addEventListener('click', function() {
    const currentChapter = parseInt(chapterSelect.value);
    const currentChapterIndex = currentBookChapters.indexOf(currentChapter);
    if (currentChapterIndex > 0) {
        const prevChapter = currentBookChapters[currentChapterIndex - 1];
        chapterSelect.value = prevChapter;
        loadVerses(selectedBookName, prevChapter);
    } else {
           console.log('Estás en el primer capítulo.');
    }
});

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    populateCharacterSelect();
     addMessageToChat("¡Hola! Selecciona un personaje para conversar sobre temas cristianos.", 'system');
});