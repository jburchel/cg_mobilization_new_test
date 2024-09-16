document.addEventListener('DOMContentLoaded', function() {
    let draggedItem = null;
    let sourceStage = null;

    function initDragAndDrop() {
        document.querySelectorAll('.church-card').forEach(card => {
            card.setAttribute('draggable', 'true');
            card.addEventListener('dragstart', function(e) {
                draggedItem = this;
                sourceStage = this.closest('.pipeline-stage');
                setTimeout(() => this.style.opacity = '0.5', 0);
            });

            card.addEventListener('dragend', function() {
                this.style.opacity = '1';
            });
        });

        document.querySelectorAll('.pipeline-stage').forEach(stage => {
            stage.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drag-over');
            });

            stage.addEventListener('dragleave', function() {
                this.classList.remove('drag-over');
            });

            stage.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                if (draggedItem && this !== sourceStage) {
                    const newStage = this.dataset.stage;
                    updateChurchStage(draggedItem.dataset.churchId, newStage, this, sourceStage);
                }
            });
        });
    }

    function updateChurchStage(churchId, newStage, targetStage, sourceStage) {
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
                console.log('Successfully updated church stage');
                targetStage.querySelector('.stage-content').appendChild(draggedItem);
                updatePipelineSummary();
            } else {
                console.error('Failed to update church stage:', data.error);
                sourceStage.querySelector('.stage-content').appendChild(draggedItem);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            sourceStage.querySelector('.stage-content').appendChild(draggedItem);
        });
    }

    function updatePipelineSummary() {
        fetch('/get-pipeline-summary/')
        .then(response => response.json())
        .then(data => {
            const summaryContainer = document.querySelector('.pipeline-summary-container');
            // Update the summary HTML here based on the received data
            // You may need to adjust this based on your exact HTML structure
        })
        .catch(error => {
            console.error('Error updating pipeline summary:', error);
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

    initDragAndDrop();
});