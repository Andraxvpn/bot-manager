function runBot(botId) {
    fetch(`/run_bot/${botId}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          document.getElementById(`bot-${botId}-status`).innerText = 'Running';
      }).catch(error => console.error('Error running bot:', error));
}

function stopBot(botId) {
    fetch(`/stop_bot/${botId}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          document.getElementById(`bot-${botId}-status`).innerText = 'Stopped';
      }).catch(error => console.error('Error stopping bot:', error));
}

function viewLogs(botId) {
    fetch(`/view_logs/${botId}`)
        .then(response => response.json())
        .then(data => {
            alert(`Log for bot ${botId}: \n${data.logs}`);
        }).catch(error => console.error('Error fetching logs:', error));
}
