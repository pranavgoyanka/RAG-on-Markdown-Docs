document.getElementById('uploadForm').addEventListener('submit', function(event) {
  event.preventDefault();
  
  let formData = new FormData();
  formData.append('file', document.getElementById('fileInput').files[0]);

  fetch('/upload', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById('uploadResponse').innerText = data.message;
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
      chatLog.innerHTML += `<p>${data.response}</p>`;
      document.getElementById('chatInput').value = '';
  })
  .catch(error => {
      console.error('Error:', error);
  });
});

document.getElementById('toggleRAG').addEventListener('click', function() {
    fetch('/toggle_rag', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('toggleRAG').innerText = data.rag_enabled ? "Disable RAG" : "Enable RAG";
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
