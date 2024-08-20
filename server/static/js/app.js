document.getElementById('uploadResponse').style.visibility = 'hidden';

fetch('/get_rag_status', {
    method: 'GET',
})
.then(response => response.json())
.then(data => {
    document.getElementById('enableRAGLabel').innerText = data.rag_enabled ? "Disable RAG" : "Enable RAG";
    document.getElementById('toggleRAG').checked = data.rag_enabled;
})
.catch(error => {
    console.error('Error:', error);
});


document.getElementById('fileInput').addEventListener('change', function(event) {
  event.preventDefault();
  
  let formData = new FormData();
  formData.append('file', document.getElementById('fileInput').files[0]);
  console.log(formData)
  fetch('/upload', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById('uploadResponse').innerText = data.message;
      document.getElementById('uploadResponse').style.visibility = 'visible';
  })
  .catch(error => {
      console.error('Error:', error);
  });
});

document.getElementById('sendMessage').addEventListener('click', function() {
  let userMessage = document.getElementById('chatInput').value;

  fetch('/chat', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: userMessage })
  })
  .then(response => response.json())
  .then(data => {
      let chatLog = document.getElementById('chatLog');
      chatLog.innerHTML += `<p><strong>Question</strong>: ${userMessage}</p>`;
      if (data.using_rag){
          chatLog.innerHTML += `<p><strong>Response (<em>RAG Enabled</em>)</strong>: ${data.response}</p>`;
      } else {
          chatLog.innerHTML += `<p><strong>Response</strong>: ${data.response}</p>`;
      }
      document.getElementById('chatInput').value = '';
  })
  .catch(error => {
      console.error('Error:', error);
  });
});


document.getElementById("toggleRAG").addEventListener('click', function() {
    fetch('/toggle_rag', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('enableRAGLabel').innerText = data.rag_enabled ? "Disable RAG" : "Enable RAG";
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById("clear-chat-button").addEventListener('click', function() {
    document.getElementById("chatLog").innerText = ""
})