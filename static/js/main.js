document.getElementById('file-input').addEventListener('change', function(e) {
    var files = e.target.files;
    var formData = new FormData();
    
    for (var i = 0; i < files.length; i++) {
        formData.append('file', files[i]);
    }

    document.getElementById('file-status').textContent = '正在读取文件内容';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('file-status').textContent = '错误: ' + data.error;
        } else {
            document.getElementById('file-status').textContent = '文件内容切分完成';
            data.files.forEach(file => addUploadedFile(file.filename));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('file-status').textContent = '上传失败';
    });
});

function addUploadedFile(filename) {
    var uploadedFiles = document.getElementById('uploaded-files');
    var li = document.createElement('li');
    li.innerHTML = `
        ${filename}
        <button class="delete-file" onclick="deleteFile('${filename}')">删除</button>
    `;
    uploadedFiles.appendChild(li);
}

function deleteFile(filename) {
    fetch('/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({filename: filename})
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'File deleted successfully') {
            var fileList = document.getElementById('uploaded-files');
            var items = fileList.getElementsByTagName('li');
            for (var i = 0; i < items.length; i++) {
                if (items[i].textContent.includes(filename)) {
                    fileList.removeChild(items[i]);
                    break;
                }
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    addMessage('user', userInput);
    document.getElementById('user-input').value = '';

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({message: userInput})
    })
    .then(response => response.json())
    .then(data => {
        addMessage('bot', data.response);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function addMessage(sender, content) {
    var chatHistory = document.getElementById('chat-history');
    var messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + (sender === 'user' ? 'user-message' : 'bot-message');
    
    var timestamp = new Date().toLocaleTimeString();
    var icon = sender === 'user' ? '👤' : '🤖';
    
    messageDiv.innerHTML = `
        <p>${icon} ${timestamp}</p>
        <div>${sender === 'bot' ? marked.parse(content) : content}</div>
    `;
    
    if (sender === 'bot') {
        var copyButton = document.createElement('button');
        copyButton.textContent = '复制';
        copyButton.className = 'copy-button';
        copyButton.onclick = function() {
            navigator.clipboard.writeText(content).then(function() {
                copyButton.textContent = '已复制';
                setTimeout(function() {
                    copyButton.textContent = '复制';
                }, 2000);
            });
        };
        messageDiv.appendChild(copyButton);
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function clearChat() {
    document.getElementById('chat-history').innerHTML = '';
}

document.getElementById('user-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById('send-button').addEventListener('click', sendMessage);
