function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.getAttribute('data-church-id'));
}

function drop(ev) {
    ev.preventDefault();
    var churchId = ev.dataTransfer.getData("text");
    var draggedElement = document.querySelector(`[data-church-id="${churchId}"]`);
    var targetStage = ev.target.closest('.pipeline-stage');
    
    if (targetStage && draggedElement) {
        var newStage = targetStage.getAttribute('data-stage');
        var oldStage = draggedElement.closest('.pipeline-stage').getAttribute('data-stage');
        
        if (newStage !== oldStage) {
            targetStage.querySelector('.stage-content').appendChild(draggedElement);
            updateChurchStage(churchId, newStage);
        }
    }
}

function updateChurchStage(churchId, newStage) {
    // Send an AJAX request to update the church's stage in the backend
    fetch('/update-church-stage/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            church_id: churchId,
            new_stage: newStage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Church stage updated successfully');
            updatePipelineSummary();
        } else {
            console.error('Failed to update church stage');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

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

function updatePipelineSummary() {
    // Fetch updated summary data from the server
    fetch('/get-pipeline-summary/')
    .then(response => response.json())
    .then(data => {
        // Update the summary in the DOM
        const summaryContainer = document.querySelector('.pipeline-summary-container');
        // Update the summary HTML here based on the received data
        // You may need to adjust this based on your exact HTML structure
    })
    .catch(error => {
        console.error('Error updating pipeline summary:', error);
    });
}

// Add event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const churchCards = document.querySelectorAll('.church-card');
    const pipelineStages = document.querySelectorAll('.pipeline-stage');

    churchCards.forEach(card => {
        card.addEventListener('dragstart', drag);
    });

    pipelineStages.forEach(stage => {
        stage.addEventListener('dragover', allowDrop);
        stage.addEventListener('drop', drop);
    });
});